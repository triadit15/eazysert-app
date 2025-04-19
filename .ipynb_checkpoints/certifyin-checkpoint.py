import os
from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import datetime

# Set paths
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Users\User\Documents\Poppler-24.08.0\Library\bin'

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Initialize app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def add_certification_stamp(image_path):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Use default font
    font = ImageFont.load_default()
    
    stamp_text = f"CERTIFIED\n{datetime.datetime.now().strftime('%Y-%m-%d')}"
    draw.text((50, 50), stamp_text, fill="red", font=font)

    certified_path = image_path.replace(".jpg", "_certified.jpg")
    image.save(certified_path)
    return certified_path

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "No file part"
    
    file = request.files['pdf']
    if file.filename == '':
        return "No selected file"
    
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    try:
        pages = convert_from_path(pdf_path, 500, poppler_path=POPPLER_PATH)
        image_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
        pages[0].save(image_path, 'JPEG')

        extracted_text = pytesseract.image_to_string(Image.open(image_path))

        certified_image = add_certification_stamp(image_path)

        return render_template('result.html', text=extracted_text, image_path=certified_image)
    
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/download')
def download_certified():
    certified_path = os.path.join(OUTPUT_FOLDER, 'page1_certified.jpg')
    return send_file(certified_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)