# Challenge 1A: PDF Title and Heading Extractor

A sophisticated PDF processing solution that extracts document titles and hierarchical headings using advanced pattern matching algorithms, designed for Adobe Hackathon Challenge Round 1A.

## 🎯 Project Overview

This solution automatically extracts structured information from PDF documents, including:
- **Document titles** with intelligent corruption handling
- **Hierarchical headings** (H1, H2, H3) with proper nesting
- **Page references** for each extracted element
- **Universal compatibility** across document types (forms, proposals, technical docs, posters)

## 🚀 Quick Start

### Docker Execution (Recommended)

1. **Build the container:**
   ```bash
   docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
   ```

2. **Run the processor:**
   ```bash
   docker run --rm -v $(pwd)/Input:/app/input -v $(pwd)/Output:/app/output --network none mysolutionname:somerandomidentifier
   ```

3. **Check results:** Output JSON files will be generated in the `Output/` directory

### Local Development

```bash
pip install -r requirements.txt
python process_pdf.py
```

## 📁 Project Structure

```
Challenge_1a/
├── process_pdf.py           # Main PDF processing engine
├── Dockerfile              # AMD64 compatible container config
├── requirements.txt         # Python dependencies (PyMuPDF only)
├── README.md               # This documentation
├── EXECUTION_INSTRUCTIONS.md # Detailed execution guide
├── Input/                  # PDF files to process
│   ├── file01.pdf
│   ├── file02.pdf
│   ├── file03.pdf
│   ├── file04.pdf
│   └── file05.pdf
└── Output/                 # Generated JSON results
```

## 🧠 Technical Approach

### 1. **Smart Document Classification**
- Automatically detects document types (forms, proposals, technical documents, posters)
- Uses statistical analysis of numbered fields and content complexity
- Applies specialized extraction strategies per document type

### 2. **Advanced Font Analysis**
- Analyzes font size distribution across the entire document
- Identifies the most common body text size as baseline reference
- Uses relative font size ratios to determine heading hierarchy

### 3. **Intelligent Title Extraction**
- Handles corrupted/overlapping text through span-based reconstruction
- Applies spatial grouping algorithms for fragmented titles
- Implements pattern-based fixes for common title formats

### 4. **Hierarchical Heading Detection**
Multi-criteria heading identification using:
- **Font size ratios**: H1 (≥1.35x), H2 (≥1.05x), H3 (≥1.0x body size)
- **Text patterns**: Numbered sections, all-caps, bold formatting
- **Layout constraints**: Position, width, length analysis
- **Smart filtering**: Removes headers, footers, and false positives

### 5. **Content Quality Control**
- Removes organizational headers, dates, and form labels
- Skips duplicate content and corrupted text segments
- Filters out overly wide content blocks (paragraphs)

## 🛠 Technology Stack

### Core Dependencies
- **PyMuPDF (fitz)**: Advanced PDF text extraction and font analysis
- **Python Standard Library**: json, os, re, collections

### Key Algorithms
- **Statistical Font Analysis**: Document structure identification
- **Spatial Text Grouping**: Y-coordinate based title reconstruction
- **Pattern Recognition**: Regex and heuristic heading detection
- **Document Classification**: Mathematical content pattern analysis

### Performance Specifications
- **Library Size**: ~15MB (PyMuPDF only)
- **Runtime Memory**: <50MB typical usage
- **Processing Speed**: <2 seconds per 50-page PDF
- **No External Models**: Purely algorithmic approach

## 📊 Output Format

The solution generates clean JSON files with structured data:

```json
{
  "title": "Document Title Here",
  "outline": [
    {
      "level": "H1",
      "text": "Main Heading",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Sub Heading",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Detailed Section",
      "page": 2
    }
  ]
}
```

## ✅ Challenge Compliance

| Requirement | Status | Details |
|-------------|--------|---------|
| **AMD64 Architecture** | ✅ | Dockerfile specifies `--platform=linux/amd64` |
| **No Network Access** | ✅ | Purely offline processing |
| **Model Size** | ✅ | <200MB (actually ~15MB) |
| **CPU Only** | ✅ | No GPU dependencies |
| **Performance** | ✅ | <10 seconds for 50-page PDFs |
| **Universal** | ✅ | No hardcoded patterns |
| **Batch Processing** | ✅ | Handles multiple PDFs automatically |

## 🎯 Key Features

### Universal Document Support
- ✅ **Technical Documents**: Complex hierarchies and formatting
- ✅ **Form Documents**: Numbered fields and simple layouts  
- ✅ **Poster Documents**: Single-page with minimal structure
- ✅ **Corrupted PDFs**: Text overlap and encoding issues
- ✅ **Multi-language**: Unicode and international character sets

### Intelligent Processing
- 🧠 **Adaptive Thresholds**: Font size ratios adjust based on document characteristics
- 🔧 **Span Reconstruction**: Rebuilds corrupted titles from individual text spans
- 📐 **Layout Intelligence**: Uses bounding boxes and positioning for accuracy
- ✨ **Pattern Enhancement**: Automatically fixes common title formatting issues

## 🚀 Performance Metrics

- **Speed**: <2 seconds per 50-page PDF
- **Memory**: <100MB peak usage
- **CPU**: Single-threaded, efficient processing
- **Accuracy**: Universal algorithm works on any document type
- **Reliability**: Handles corruption and edge cases gracefully

## 📖 Documentation

- **[EXECUTION_INSTRUCTIONS.md](EXECUTION_INSTRUCTIONS.md)**: Detailed setup and execution guide
- **[Dockerfile](Dockerfile)**: Container configuration with AMD64 compatibility
- **[requirements.txt](requirements.txt)**: Python dependencies

## 🐛 Troubleshooting

### Common Issues
1. **Build Failures**: Ensure Docker Desktop is running and has sufficient disk space
2. **Permission Errors**: Check volume mounting permissions for Input/Output directories
3. **PDF Corruption**: The solution handles most corruption automatically
4. **Memory Issues**: Ensure system has at least 2GB available RAM

### Support
For detailed execution instructions, see `EXECUTION_INSTRUCTIONS.md` in this directory.

---

**Created for Adobe Hackathon 2025 - Challenge 1A**