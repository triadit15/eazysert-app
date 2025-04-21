FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies including Poppler
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "databasesql:app"]