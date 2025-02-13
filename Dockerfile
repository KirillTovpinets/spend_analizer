# Use an official Python runtime as a base image
FROM python:3.8-slim

# Install Tesseract and required packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/

# Optionally, install additional language packs for Tesseract
# RUN apt-get install -y tesseract-ocr-rus tesseract-ocr-spa

# Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app's code into the container
COPY . /app/

# Set environment variable for Tesseract's data path
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Expose port if needed
EXPOSE 5000

# Command to run your app
CMD ["gunicorn", "spend_analizer.wsgi:application"]
