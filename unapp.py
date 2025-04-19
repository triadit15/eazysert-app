from flask import Flask, render_template, request, send_from_directory
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Paths to dependencies
POPPLER_PATH = r'C:\Users\User\Documents\poppler-24.08.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Save uploaded PDF
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded.pdf')
    file.save(pdf_path)

    # Convert first page of PDF to image
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    first_page_image = images[0]

    # Save input image (optional)
    input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_page1.jpg')
    first_page_image.save(input_image_path, 'JPEG')

    # Add certification stamp
    stamped_image = first_page_image.copy()
    draw = ImageDraw.Draw(stamped_image)
    font = ImageFont.load_default()
    stamp_text = "Certified by Eazy Cert"
    draw.text((10, 10), stamp_text, font=font, fill=(255, 0, 0))

    # Save stamped image
    stamped_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'stamped_page1.jpg')
    stamped_image.save(stamped_image_path)

    # OCR
    extracted_text = pytesseract.image_to_string(first_page_image)

    return render_template('result.html', text=extracted_text, image_path='stamped_page1.jpg')

@app.route('/static/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)