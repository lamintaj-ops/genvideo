FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with explicit versions (no cache to ensure latest)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "huggingface-hub==0.23.0" \
    gradio==4.19.2 \
    "imageio[ffmpeg]>=2.9.0" \
    "pillow>=10.0.0" \
    "pandas>=2.0.0" \
    "numpy>=1.24.0" \
    "requests>=2.28.0"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p output/jobs temp temp_edit temp_outro_check static/uploads

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Set environment variables for Gradio
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["python", "app.py"]