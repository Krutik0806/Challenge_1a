# Use AMD64 compatible Python base image as required
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main processing script
COPY process_pdf.py .

# Create input and output directories as expected by the challenge
RUN mkdir -p /app/input /app/output

# Set the default command to run the PDF processor
CMD ["python", "process_pdf.py"]