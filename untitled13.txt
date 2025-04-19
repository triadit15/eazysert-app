import os
import re
import datetime
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# Paths to executables
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Users\User\Documents\Poppler-24.08.0\Library\bin'

# Folder paths
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Identity database
verified_ids = {
    "0202155519087": "Siyabonga Shipalana",
    "9102026009181": "Ayanda Sithole",
    "8503037009384": "Thabo Dlamini"
}

# Flask app config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def find_sa_id(text):
    """Finds a 13-digit SA ID in extracted text."""
    match = re.search(r'\b\d{13}\b', text)
    return match.group() if match else None

def add_certification_stamp(image_path):
    """Adds a certification stamp in the center of the image."""
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf', size=80)
    except:
        font = ImageFont.load_default()

    stamp_lines = [
        "CERTIFIED BY EAZY CERT",
        datetime.datetime.now().strftime('%Y-%m-%d')
    ]

    # Measure manually
    line_spacing = 20
    line_sizes = [font.getsize(line) for line in stamp_lines]
    text_width = max(w for w, h in line_sizes)
    text_height = sum(h for w, h in line_sizes) + (len(stamp_lines) - 1) * line_spacing

    image_width, image_height = image.size
    x = (image_width - text_width) / 2
    y = (image_height - text_height) / 2

    padding = 40
    draw.rectangle(
        [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
        fill="white",
        outline="red",
        width=5
    )

    current_y = y
    for line in stamp_lines:
        draw.text((x, current_y), line, fill="red", font=font)
        current_y += font.getsize(line)[1] + line_spacing

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
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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
    return send_file(certified_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)