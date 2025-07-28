# PDF Processing Solution - Execution Instructions

## Prerequisites

1. **Docker Desktop** must be installed and running on your system

   - Download from: https://www.docker.com/products/docker-desktop/
   - Ensure Docker Desktop is started before proceeding

2. **Input Files Setup**
   - Place all PDF files to be processed in the `Input/` directory
   - Ensure the `Output/` directory exists (it will be created if missing)

## Directory Structure

```
Challenge_1a/
├── Dockerfile
├── process_pdf.py
├── requirements.txt
├── README.md
├── EXECUTION_INSTRUCTIONS.md
├── Input/
│   ├── file01.pdf
│   ├── file02.pdf
│   └── ... (your PDF files)
└── Output/
    └── (JSON files will be generated here)
```

## Step-by-Step Execution Instructions

### Step 1: Open Terminal/Command Prompt

- **Windows**: Open PowerShell or Command Prompt
- **macOS/Linux**: Open Terminal

### Step 2: Navigate to Project Directory

```bash
cd path/to/Challenge_1a
```

Replace `path/to/Challenge_1a` with the actual path to your project directory.

### Step 3: Build the Docker Image

Execute the following command to build the Docker image:

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

**Expected Output:**

- The build process will download the Python base image
- Install system dependencies (gcc, g++)
- Install Python dependencies (PyMuPDF)
- Copy the processing script
- Create input/output directories

### Step 4: Run the Docker Container

Execute the following command to process the PDF files:

**For Unix/Linux/macOS:**

```bash
docker run --rm -v $(pwd)/Input:/app/input -v $(pwd)/Output:/app/output --network none mysolutionname:somerandomidentifier
```

**For Windows PowerShell:**

```powershell
docker run --rm -v "${PWD}/Input:/app/input" -v "${PWD}/Output:/app/output" --network none mysolutionname:somerandomidentifier
```

**For Windows Command Prompt:**

```cmd
docker run --rm -v "%cd%/Input:/app/input" -v "%cd%/Output:/app/output" --network none mysolutionname:somerandomidentifier
```

### Step 5: Verify Results

After execution, check the `Output/` directory for generated JSON files:

```bash
# List output files
ls Output/

# Or on Windows
dir Output\
```

## Command Explanation

### Build Command Parameters:

- `--platform linux/amd64`: Ensures compatibility across different architectures
- `-t mysolutionname:somerandomidentifier`: Tags the image with the specified name
- `.`: Uses the current directory as build context

### Run Command Parameters:

- `--rm`: Automatically removes the container after execution
- `-v $(pwd)/Input:/app/input`: Mounts local Input directory to container's /app/input
- `-v $(pwd)/Output:/app/output`: Mounts local Output directory to container's /app/output
- `--network none`: Disables network access for security
- `mysolutionname:somerandomidentifier`: The image name to run

## Expected Processing Output

The container will display progress messages like:

```
✅ Processed: file01.pdf
✅ Processed: file02.pdf
✅ Processed: file03.pdf
...
```

## Output Format

For each PDF file processed, a corresponding JSON file will be generated in the `Output/` directory with the following structure:

```json
{
  "title": "Document Title",
  "headings": ["Heading 1", "Heading 2", "Subheading 2.1"]
}
```

## Performance

- **Execution Time**: ≤ 10 seconds for a 50-page PDF
- **Current Performance**: ~0.07 seconds per page
- **Memory Usage**: Optimized for minimal memory footprint

## Troubleshooting

### Docker Not Running

```
ERROR: error during connect: ... docker daemon not running
```

**Solution**: Start Docker Desktop application

### Permission Issues (Linux/macOS)

```
Permission denied
```

**Solution**: Add `sudo` before docker commands or add user to docker group

### Path Issues (Windows)

```
Invalid volume specification
```

**Solution**: Use full paths or ensure you're in the correct directory

### No Files Found

```
No PDF files found in input directory
```

**Solution**: Ensure PDF files are placed in the `Input/` directory

## Verification Commands

### Check Docker Image

```bash
docker images mysolutionname:somerandomidentifier
```

### Check Container Logs (if needed)

```bash
docker logs <container_id>
```

### Validate Output Files

```bash
# Check file count
ls -la Output/ | wc -l

# Validate JSON format
python -m json.tool Output/file01.json
```

## Clean Up (Optional)

To remove the Docker image after use:

```bash
docker rmi mysolutionname:somerandomidentifier
```

## Support

- Ensure all PDF files are readable and not corrupted
- Check that the Input directory contains valid PDF files
- Verify Docker Desktop has sufficient resources allocated
- For large files, monitor system memory usage

---

**Note**: This solution is optimized for performance and meets the requirement of processing a 50-page PDF in ≤ 10 seconds.
