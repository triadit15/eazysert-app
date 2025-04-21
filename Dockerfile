# Use an official Python image
FROM python:3.10-slim

# Install Poppler and other dependencies
RUN apt-get update && \
    apt-get install -y poppler-utils tesseract-ocr && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start the app with gunicorn
CMD ["gunicorn", "databasesql:app", "--bind", "0.0.0.0:8000"]