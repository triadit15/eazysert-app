from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set up Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set upload folder in config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to Tesseract OCR EXE
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to Poppler bin
POPPLER_PATH = r'C:\Users\User\Documents\Poppler-24.08.0\Library\bin'

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pdf_path)

    try:
        # Convert PDF to image
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        first_page = images[0]
        output_image_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
        first_page.save(output_image_path, 'JPEG')

        # OCR using Tesseract
        extracted_text = pytesseract.image_to_string(Image.open(output_image_path))
        return f"<h3>Extracted Text:</h3><pre>{extracted_text}</pre>"

    except Exception as e:
        return f"Error extracting text: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)