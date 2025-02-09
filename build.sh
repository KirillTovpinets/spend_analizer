#!/bin/bash

# Update the package list
sudo apt-get update

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr

# Install additional language packs for Tesseract if necessary (optional)
# sudo apt-get install -y tesseract-ocr-eng tesseract-ocr-other-language

# You can also install other necessary dependencies for your app here
# For example, installing Python dependencies via pip:
pip install -r requirements.txt
