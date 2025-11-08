# Use Python 3.11 (more compatible than 3.13 for Docker)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data reports data/models

# Make scripts executable
RUN chmod +x demo_free.py

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command - run dashboard
CMD ["streamlit", "run", "src/dashboard_simple.py", "--server.address", "0.0.0.0", "--server.port", "8501"]