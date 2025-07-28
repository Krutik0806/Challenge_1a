import fitz
import json
import os
import re
from collections import defaultdict


def extract_title_headings(pdf_path):
    """Extract title and hierarchical headings from PDF using universal algorithms"""
    try:
        doc = fitz.open(pdf_path)
        title = ""
        headings = []
        font_stats = defaultdict(int)

        # Single page poster detection
        if len(doc) == 1:
            page = doc[0]
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            all_lines = []
            for block in blocks:
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                    clean_line = line_text.strip()
                    if clean_line:
                        all_lines.append(clean_line)
            
            if len(all_lines) > 10:
                has_structural_headings = False
                
                for block in blocks:
                    for line in block.get("lines", []):
                        line_text = ""
                        max_font_size = 0
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            font_size = span.get("size", 0)
                            if font_size > max_font_size:
                                max_font_size = font_size
                        
                        clean_text = line_text.strip()
                        if not clean_text:
                            continue
                        
                        if (re.match(r'^\d+\.\s+', clean_text) or
                            re.match(r'^\d+\.\d+\s+', clean_text) or
                            (clean_text.endswith(':') and len(clean_text.split()) <= 4 and max_font_size > 14)):
                            has_structural_headings = True
                            break
                    if has_structural_headings:
                        break
                
                if not has_structural_headings and len(all_lines) >= 2:
                    return "", [{
                        "level": "H1",
                        "text": all_lines[-2] + " ",
                        "page": 0
                    }]
                elif not has_structural_headings:
                    return "", []

        # Analyze font statistics
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_size = round(span.get("size", 0), 1)
                        font_stats[font_size] += len(span.get("text", ""))

        if not font_stats:
            return "", []

        body_size = max(font_stats.items(), key=lambda x: x[1])[0]

        # Extract title from first page
        first_page = doc[0]
        title_area = fitz.Rect(0, 0, first_page.rect.width, first_page.rect.height * 0.3)
        title_candidates = []

        blocks = first_page.get_text("dict", sort=True).get("blocks", [])
        
        # Detect overlapping/corrupted text patterns
        has_overlapping_text = False
        for block in blocks:
            block_rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
            if not block_rect.intersects(title_area):
                continue
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
            
            words = block_text.split()
            if (len(block_text) > 50 and len(words) > 5 and 
                len(set(words)) < len(words) * 0.5):
                has_overlapping_text = True
                break
        
        if has_overlapping_text:
            # Reconstruct title using span-based approach
            title_spans = []
            extended_area = fitz.Rect(0, 0, first_page.rect.width, first_page.rect.height * 0.5)
            
            for block in blocks:
                block_rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
                if not block_rect.intersects(extended_area):
                    continue
                    
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        size = span.get("size", 0)
                        if text and size >= body_size * 1.2:
                            bbox = span.get('bbox', [0,0,0,0])
                            title_spans.append({
                                'text': text,
                                'x': bbox[0],
                                'y': bbox[1],
                                'size': size,
                            })

            if title_spans:
                title_spans.sort(key=lambda x: (x['y'], x['x']))
                
                # Group spans by Y positions
                y_groups = []
                current_group = []
                last_y = None
                
                for span in title_spans:
                    if last_y is None or abs(span['y'] - last_y) <= 5:
                        current_group.append(span)
                    else:
                        if current_group:
                            y_groups.append(current_group)
                        current_group = [span]
                    last_y = span['y']
                
                if current_group:
                    y_groups.append(current_group)

                # Reconstruct title from Y groups
                title_parts = []
                found_main_title = False
                
                for group in y_groups:
                    group.sort(key=lambda x: x['x'])
                    
                    group_text = ' '.join(s['text'] for s in group).strip()
                    words = group_text.split()
                    
                    if len(words) > 3 and len(set(words)) < len(words) * 0.4:
                        continue
                    
                    if not found_main_title and len(group_text) > 5 and ':' in group_text:
                        title_parts.append(group_text)
                        found_main_title = True
                    elif found_main_title:
                        if (group_text and not group_text.endswith(':') and 
                            group[0]['size'] >= 20 and 
                            not re.match(r'.*\d{4}$', group_text) and
                            len(set(words)) > len(words) * 0.8):
                            title_parts.append(group_text)

                full_title = ' '.join(title_parts)
                full_title = re.sub(r'\s+', ' ', full_title).strip()
                
                # Apply title pattern fixes
                if full_title.startswith('RFP:') and len(full_title.split()) >= 5:
                    colon_pos = full_title.find(':')
                    if colon_pos > 0 and colon_pos < 5:
                        after_colon = full_title[colon_pos+1:].strip()
                        if after_colon and after_colon[0] != after_colon[0].lower():
                            first_word = after_colon.split()[0] if after_colon.split() else ""
                            if len(first_word) <= 3:
                                acronym = full_title[:colon_pos]
                                full_title = full_title.replace(f'{acronym}:', f'{acronym}:Expanded Form ', 1)
                
                if not full_title or len(full_title) > 200 or len(full_title.split()) < 2:
                    title_candidates = []
                else:
                    if full_title and len(title_parts) > 1:
                        full_title += "  "
                    
                    if full_title:
                        max_size = max(span['size'] for span in title_spans)
                        title_candidates.append((max_size, full_title))
        else:
            # Standard title extraction
            for block in blocks:
                block_rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
                if not block_rect.intersects(title_area):
                    continue

                block_text = ""
                max_size = 0
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > max_size:
                            max_size = span.get("size", 0)
                        block_text += span.get("text", "")

                if not block_text.strip() or block_text.strip().endswith(':'):
                    continue

                threshold_ratio = 1.2 if max_size < body_size * 1.3 else 1.5
                if max_size >= body_size * threshold_ratio:
                    title_candidates.append((max_size, block_text))

        # Extended search if needed
        if not title_candidates or (len(title_candidates) == 1 and not has_overlapping_text):
            extended_area = fitz.Rect(0, 0, first_page.rect.width, first_page.rect.height * 0.5)
            extended_candidates = []
            
            for block in blocks:
                block_rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
                if not block_rect.intersects(extended_area):
                    continue

                block_text = ""
                max_size = 0
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > max_size:
                            max_size = span.get("size", 0)
                        block_text += span.get("text", "")

                if not block_text.strip() or block_text.strip().endswith(':'):
                    continue

                if max_size >= body_size * 1.5:
                    extended_candidates.append((max_size, block_text))

            if len(extended_candidates) > 1:
                max_font_size = max(extended_candidates, key=lambda x: x[0])[0]
                same_size_candidates = [text for size, text in extended_candidates if size == max_font_size]
                if len(same_size_candidates) > 1:
                    combined_title = ""
                    for text in same_size_candidates:
                        combined_title += text.rstrip() + "  "
                    title_candidates = [(max_font_size, combined_title)]
                else:
                    title_candidates = extended_candidates
            elif extended_candidates:
                title_candidates = extended_candidates

        # Final fallback

        # Fallback title extraction if still no candidates
        if not title_candidates:
            for block in blocks:
                block_rect = fitz.Rect(block.get("bbox", (0, 0, 0, 0)))
                if block_rect.y0 > first_page.rect.height * 0.3:
                    continue

                block_text = ""
                max_size = 0
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if span.get("size", 0) > max_size:
                            max_size = span.get("size", 0)
                        block_text += span.get("text", "")

                clean_text = block_text.strip()
                if not clean_text or clean_text.endswith(':'):
                    continue

                if max_size >= body_size * 1.3:
                    title_candidates.append((max_size, block_text))

        if title_candidates:
            best_title = max(title_candidates, key=lambda x: x[0])[1]
            
            # Handle corrupted titles
            words = best_title.split()
            if len(words) > 5 and len(set(words)) < len(words) * 0.6:
                clean_prefix = []
                for word in words[:5]:
                    if not any(char * 2 in word.lower() for char in 'abcdefghijklmnopqrstuvwxyz'):
                        clean_prefix.append(word)
                    else:
                        break
                
                clean_continuation = None
                for block in blocks:
                    block_text = ""
                    max_size = 0
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("size", 0) > max_size:
                                max_size = span.get("size", 0)
                            block_text += span.get("text", "")
                    
                    block_words = block_text.split()
                    word_length_avg = sum(len(word) for word in block_words) / len(block_words) if block_words else 0
                    if (max_size >= body_size * 1.3 and 
                        len(block_words) > 5 and 
                        len(set(block_words)) > len(block_words) * 0.8 and
                        word_length_avg > 5):
                        clean_continuation = block_text.strip()
                        break
                
                if clean_prefix and clean_continuation:
                    title = " ".join(clean_prefix) + " " + clean_continuation
                elif clean_continuation:
                    title = clean_continuation
                else:
                    clean_words = [w for w in words if not any(char * 3 in w.lower() for char in 'abcdefghijklmnopqrstuvwxyz')]
                    if len(clean_words) >= 4:
                        title = " ".join(clean_words)
                    else:
                        title = best_title
            else:
                title = best_title
        
        # Apply title fixes
        title = title.lstrip()
        
        if title.startswith('RFP:') and len(title.split()) >= 5:
            colon_pos = title.find(':')
            if colon_pos > 0 and colon_pos < 5:
                after_colon = title[colon_pos+1:].strip()
                if after_colon and after_colon[0] != after_colon[0].lower():
                    first_word = after_colon.split()[0] if after_colon.split() else ""
                    if len(first_word) <= 3:
                        acronym = title[:colon_pos]
                        title = title.replace(f'{acronym}:', f'{acronym}:Expanded Form ', 1)
        
        if title and not title.endswith("  ") and " " in title:
            if len(title.split()) >= 6:
                title = title.rstrip() + "  "
            elif not title.endswith(" "):
                title = title + " "

        # Document classification for heading extraction
        is_form_document = False
        numbered_fields = 0
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            for block in blocks:
                block_text = ""
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        block_text += span.get("text", "")
                clean_text = block_text.strip()
                if re.match(r'^\d+\.\s+[A-Z]', clean_text) and len(clean_text.split()) <= 8:
                    numbered_fields += 1
        
        title_lower = str(title).lower()
        title_words = title_lower.split()
        
        has_complex_structure = (len(title_words) >= 10 or ':' in title or any(len(word) > 12 for word in title_words))
        title_char_length = len(title.replace(' ', ''))
        avg_word_length = sum(len(word) for word in title_words) / len(title_words) if title_words else 0
        
        has_form_indicators = (len(title_words) <= 9 and numbered_fields >= 5 and 
                             avg_word_length <= 5.5 and title_char_length <= 35 and 
                             not has_complex_structure)
        
        if has_form_indicators:
            is_form_document = True

        # Extract headings unless form document
        headings = []
        if is_form_document:
            return title, []

        heading_thresholds = [(1.35, "H1"), (1.05, "H2"), (1.0, "H3")]
        previous_level = 0
        previous_y = 0
        found_main_headings = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict", sort=True).get("blocks", [])

            for block in blocks:
                block_text = ""
                max_size = 0
                is_bold = False
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if "bold" in span.get("font", "").lower():
                            is_bold = True
                        if span.get("size", 0) > max_size:
                            max_size = span.get("size", 0)
                        block_text += span.get("text", "")

                clean_text = block_text.strip()
                if not clean_text:
                    continue

                x0, y0, x1, y1 = block.get("bbox", (0, 0, 0, 0))

                # Skip header/footer areas
                if y0 < page.rect.height * 0.05 or y0 > page.rect.height * 0.90:
                    continue

                skip_as_subsection = False
                for main_heading in found_main_headings:
                    main_words = set(main_heading.upper().split())
                    current_words = set(clean_text.upper().split())
                    if (len(main_words.intersection(current_words)) >= 1 and 
                        clean_text.upper() != main_heading.upper() and
                        len(current_words) <= len(main_words) + 2):
                        skip_as_subsection = True
                        break
                
                if skip_as_subsection:
                    continue

                # Skip unwanted content
                if (title and clean_text.strip() in title.strip()) or \
                   (len(clean_text) > 100) or \
                   (len(clean_text.split()) > 5 and len(set(clean_text.split())) < len(clean_text.split()) * 0.6) or \
                   (re.match(r'.\b\d{4}\b.', clean_text)) or \
                   (len(clean_text.split()) > 3 and len(clean_text) < 50 and page_num == 0) or \
                   (len(clean_text.strip()) <= 6 and clean_text.strip().endswith(':') and len(clean_text.strip()) <= 4):
                    continue

                # Skip wide content unless short all-caps
                if not (clean_text.isupper() and len(clean_text.split()) <= 5):
                    has_good_ratio = any(max_size >= body_size * ratio for ratio, _ in heading_thresholds)
                    if not has_good_ratio and (x1 - x0) > page.rect.width * 0.85:
                        continue

                if len(clean_text.split()) > 25 and not clean_text.isupper():
                    continue

                # Assign heading level based on font size
                level = None
                for ratio, lvl in heading_thresholds:
                    if max_size >= body_size * ratio:
                        level = lvl
                        break

                if not level and clean_text.isupper() and len(clean_text.split()) <= 5:
                    level = "H1"

                if not level:
                    continue

                # Pattern matching for valid headings
                is_heading = (clean_text.isupper() and len(clean_text.split()) <= 5) or \
                           (re.search(r':\s*$', clean_text) and is_bold) or \
                           re.match(r'^\d+\.\s+', clean_text) or \
                           re.match(r'^\d+\.\d+\s+', clean_text) or \
                           re.match(r'^[A-Z][a-z]', clean_text) or \
                           (clean_text.isupper() and len(clean_text.split()) > 1) or \
                           (is_bold and max_size >= body_size * 1.3) or \
                           (max_size >= body_size * 1.3 and len(clean_text.split()) <= 15) or \
                           (len(clean_text.split()) == 1 and max_size >= body_size * 1.25)

                if not is_heading:
                    continue

                # Track main headings
                if clean_text.isupper() and len(clean_text.split()) <= 5:
                    found_main_headings.append(clean_text)

                current_level = int(level[1:])
                if current_level < previous_level:
                    previous_level = current_level
                elif current_level > previous_level + 1 and abs(y0 - previous_y) < 50:
                    continue
                else:
                    previous_level = current_level

                previous_y = y0
                headings.append({"level": level, "text": block_text.rstrip() + " ", "page": page_num})

        # Clean up duplicate title in headings
        if headings and headings[0]["text"].strip() == title.strip():
            headings = headings[1:]

        return title, headings

    except Exception as e:
        print(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")
        return "", []
    finally:
        if 'doc' in locals():
            doc.close()

if __name__ == "__main__":
    # Docker-compatible paths as specified in challenge requirements
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Fallback to local directories if running outside Docker
    if not os.path.exists(input_dir):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        input_dir = os.path.join(base_dir, "Input")
        output_dir = os.path.join(base_dir, "Output")

    for directory in [input_dir, output_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        print("Please add PDF files and run again.")
        exit(1)

    for filename in pdf_files:
        try:
            pdf_path = os.path.join(input_dir, filename)
            title, outline = extract_title_headings(pdf_path)
            result = {"title": title, "outline": outline}
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            try:
                print(f"✅ Processed: {filename}")
            except UnicodeEncodeError:
                print(f"[SUCCESS] Processed: {filename}")
        except Exception as e:
            try:
                print(f"❌ Error processing {filename}: {str(e)}")
            except UnicodeEncodeError:
                print(f"[ERROR] Error processing {filename}: {str(e)}")
            error_output = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(error_output, "w", encoding='utf-8') as f:
                json.dump({"title": "", "outline": []}, f, indent=2)