import re
import cv2
import pytesseract
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import uuid
from io import TextIOWrapper
from .forms import CSVUploadForm, CSVBofUploadForm
import csv
from datetime import datetime
from .models import Expense

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'  # Update this path as needed

def parse_receipt(text):
    # Initialize the receipt data dictionary
    print(text)
    receipt_data = {
        'total': None,
        'items': [],
        'date': None,
        'merchant': None
    }

    # Split the text into lines for easier processing
    lines = text.splitlines()

    # Extract the date using a regular expression (matches formats like "01/25/2025" or "2025-01-25")
    date_pattern = r'(\b(?:\d{1,2}[-/thstndrd]*\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.,]?\s*(?:\d{1,2},?\s*\d{4}|\d{4})|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}|\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}-\d{4}|\d{4}-\d{1,2}-\d{1,2})\b)'
    for line in lines:
        date_match = re.search(date_pattern, line)
        if date_match:
            receipt_data['date'] = date_match.group(0)
            break

    # Extract line items and prices (looks for lines with a description followed by a price)
    item_pattern = r'(.+?)\s+([$\u00A3f]?\d+\.\d{0,2})'
    for line in lines:
        item_match = re.search(item_pattern, line)
        if item_match:
            description = item_match.group(1).strip()
            price = float(item_match.group(2).replace('$', '').replace('£', '').replace('f', '').strip())
            receipt_data['items'].append({
                'description': description,
                'price': price,
                'total': price,
                'id': str(uuid.uuid4())
            })

    # Extract the total (typically a line that starts with "Total")
    total_pattern = r'(?:total|balance|total\spurchase)\s*:?\s*\$?(\d+(?:[\.\s,]+\d{2}))'
    for line in lines:
        lower_line = line.lower()
        total_match = re.search(total_pattern, lower_line)
        print(total_match)
        if total_match and 'health item' not in lower_line and 'subtotal' not in lower_line:
          # Regular expression to match the format with space between digits
          updated_string = re.sub(r'(\d+)(?:[\s,])+(\d{2})', r'\1.\2', total_match.group(1).strip())
          print(updated_string)
          receipt_data['total'] = float(updated_string)
          break

    # Extract the merchant name (first line that doesn't contain a number)
    merchant_pattern = r'(Whole Foods|Walmart|Target|Safeway|Kroger|Costco|Trader Joe\'s|Publix|Aldi|Amazon|Walgreens|CVS|Home Depot|Lowe\'s|Best Buy|Staples|Office Depot|OfficeMax|Dollar General|Dollar Tree|Family Dollar|Dollar General|Dollar Tree|Family Dollar|IKEA|Bed Bath & Beyond|Michaels|Joann|Hobby Lobby|Petco|PetSmart|Pet Supplies Plus|Chewy|Tractor Supply Co|Ace Hardware|True Value|Sherwin-Williams|Menards|Lumber Liquidators|Floor & Decor|Harbor Freight|O\'Reilly Auto Parts|AutoZone|Advance Auto Parts|NAPA Auto Parts|Pep Boys|Carquest)'

    for line in lines:
        merchant_match = re.search(merchant_pattern, line, re.IGNORECASE)
        if merchant_match:
            receipt_data['merchant'] = merchant_match.group(1)
            break
    return receipt_data


def show_image(title, img):
    plt.imshow(img, cmap='gray')
    plt.title(title)
    plt.show()

def preprocess_image(image_path):
    """
    Preprocess the image before passing to Tesseract for better OCR accuracy.
    Includes resizing, grayscaling, thresholding, denoising, and skew correction.
    """
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Resize the image (scale it up for clearer text)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


    # Apply thresholding (Binarization using Otsu's thresholding)
    _, binary_image = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove noise
    denoised_image = cv2.fastNlMeansDenoising(binary_image, None, 30, 7, 21)

    # Skew correction
    corrected_image = skew_correction(denoised_image)

    return corrected_image

def skew_correction(image):
    """
    Corrects skew in the image.
    """
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def extract_text(image):
    """
    Extract text from the preprocessed image using Tesseract OCR.
    """
    # Tesseract configuration
    config = '--oem 1 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?'

    # Convert the OpenCV image to PIL format (Tesseract works better with PIL)
    pil_image = Image.fromarray(image)

    # Extract text from the image using Tesseract
    text = pytesseract.image_to_string(pil_image, config=config, lang='eng')

    return text

def main():
    # Path to the image file
    image_path = 'receipt.jpg'  # Update with your image path

    # Preprocess the image
    processed_image = preprocess_image(image_path)

    # Extract text from the processed image
    text = extract_text(processed_image)

    # Print the extracted text
    print("Extracted Text:")
    print(text)

if __name__ == "__main__":
    main()


# Apply skew correction (example using OpenCV)
def skew_correction(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


# Function to parse and format a date to ISO format
def format_to_iso(date_string):
    try:
        # Handle various date formats and convert them to ISO format
        # Try multiple formats (you can extend this as needed)
        formats = [
            "%d/%m/%Y",  # 01/01/2020
            "%Y-%m-%d",  # 2020-01-01
            "%b %d, %Y",  # Jan 1, 2020
            "%d-%b-%Y",  # 1-Jan-2020
            "%m/%d/%Y",  # 12/31/2021
        ]

        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime("%Y-%m-%d")  # Return in ISO format
            except ValueError:
                continue
        return None  # If no format matches
    except Exception as e:
        return None


def get_bof_category(description):
    if 'APPLECARD' in description:
        return 'Apple Card'
    elif 'Fee' in description or 'FEE' in description:
        return 'Fee'
    elif 'Zelle' in description:
        return 'Zelle'
    elif 'The Marke' in description or 'THE MARKE' in description:
        return 'Rent Payment'
    elif 'MOVING' in description:
        return 'Moving Expenses'
    elif 'DISCOVER' in description:
        return 'Discover Card'
    elif 'WILLO LABS' in description or 'FOLLETT CORP' in description:
        return 'Willow Labs'
    elif 'HMFUSA.com' in description:
        return 'Hyundai Finance'
    elif 'IRS TREAS' in description or 'STATE OF' in description:
        return 'IRS'
    elif 'CREAMLY' in description:
        return 'Creamly'
    elif 'ComEd' in description:
        return 'ComEd'
    elif 'USEMBASSY' in description:
        return 'VISA'
    elif 'COINBASE' in description:
        return 'Coinbase'
    elif 'Afterpay' in description:
        return 'Afterpay'
    elif 'Amazon web serv' in description:
        return 'AWS'
    elif 'AFFIRM' in description:
        return 'Affirm'
    elif 'Uber' in description:
        return 'Uber'
    else:
        return 'Other'

def process_discover_csv(request):
    form = CSVUploadForm(request.POST, request.FILES)
    if form.is_valid():
        # Read the uploaded file
        csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
        reader = csv.reader(csv_file)

        # Skip header row (if necessary)
        next(reader, None)

        # Process each row in the CSV
        created_records_number = 0
        for row in reader:
            try:
                # Assuming the CSV columns: amount, category, description, date
                trans_date = datetime.strptime(row[0], '%m/%d/%Y')
                post_date = datetime.strptime(row[1], '%m/%d/%Y')
                merchant = row[2]
                amount = float(row[3])
                category = row[4]

                # Create a new expense entry
                _, created = Expense.objects.update_or_create(
                    amount=amount,
                    transaction_date=trans_date,
                    defaults={
                        'description': '',  # Optional - add a description if needed,
                        'category':category,
                        'merchant':merchant,
                        'post_date':post_date,
                    }
                )
                if created:
                    created_records_number += 1
            except Exception as e:
                print(f"Error processing row {row}: {e}")
        print(f"Created {created_records_number} records")
    else:
        print("Form is invalid")

def process_bof_csv(request):
    form = CSVBofUploadForm(request.POST, request.FILES)
    if form.is_valid():
        # Read the uploaded file
        csv_file = TextIOWrapper(request.FILES['csv_bof_file'].file, encoding='utf-8')
        reader = csv.reader(csv_file)

        # Skip header row (if necessary)
        next(reader, None)

        # Process each row in the CSV
        created_records_number = 0
        for row in reader:
            try:
                # Assuming the CSV columns: amount, category, description, date
                date = datetime.strptime(row[0], '%m/%d/%Y')
                description = row[1]
                if 'ATM' in description or 'Online Banking transfer' in description:
                  continue

                try:
                  try:
                    amount = float(row[2])
                  except:
                    remove_commas = row[2].replace(',', '')
                    amount = float(remove_commas)
                except:
                  amount = float(row[3])
                category = get_bof_category(description)

                _, created = Expense.objects.update_or_create(
                    amount= (0 - amount),
                    transaction_date=date,
                    defaults={
                        'description': '',
                        'category':category,
                        'merchant': description,
                        'post_date':date,
                    }
                )
                if created:
                    created_records_number += 1
            except Exception as e:
                print(f"Error processing row {row}: {e}")
        print(f"Created {created_records_number} records")
