import os
import re
import datetime
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# Configure paths
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Users\User\Documents\Poppler-24.08.0\Library\bin'

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Simulated database
verified_ids = {
    "0202155519087": "Siyabonga Shipalana87",
    "9102026009181": "Ayanda Sithole",
    "8503037009384": "Thabo Dlamini"
}

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def find_sa_id(text):
    """Finds the first 13-digit South African ID number in the text."""
    match = re.search(r'\b\d{13}\b', text)
    return match.group() if match else None

def add_certification_stamp(image_path):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Load a visible font size
    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', size=40)
    except:
        font = ImageFont.load_default()

    stamp_text = f"CERTIFIED BY EAZY CERT\n{datetime.datetime.now().strftime('%Y-%m-%d')}"
    x, y = 50, 50
    text_color = "red"
    border_color = "black"

    # Get size of text block
    text_bbox = draw.textbbox((x, y), stamp_text, font=font)
    padding = 20

    # Draw border box
    draw.rectangle(
        [text_bbox[0] - padding, text_bbox[1] - padding,
         text_bbox[2] + padding, text_bbox[3] + padding],
        outline=border_color,
        width=5
    )

    # Draw the text inside the box
    draw.multiline_text((x, y), stamp_text, fill=text_color, font=font, spacing=10)

    # Save stamped image
    certified_path = image_path.replace(".jpg", "_certified.jpg")
    image.save(certified_path)
    return certified_path

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "No file uploaded"
    
    file = request.files['pdf']
    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    try:
        pages = convert_from_path(pdf_path, 500, poppler_path=POPPLER_PATH)
        image_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
        pages[0].save(image_path, 'JPEG')

        extracted_text = pytesseract.image_to_string(Image.open(image_path))
        found_id = find_sa_id(extracted_text)

        verification_result = "Not Verified"
        certified_image = image_path

        if found_id and found_id in verified_ids:
            verification_result = f"Verified: {verified_ids[found_id]}"
            certified_image = add_certification_stamp(image_path)

        return render_template('result.html', text=extracted_text, image_path=certified_image, status=verification_result)

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/download')
def download_certified():
    certified_path = os.path.join(OUTPUT_FOLDER, 'page1_certified.jpg')