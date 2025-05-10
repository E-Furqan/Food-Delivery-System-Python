# Use official Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the FastAPI app with Uvicorn, using the PORT environment variable explicitly
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0"]