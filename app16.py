import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import fitz # PyMuPDF
from PIL import Image

UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'static/images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # Open PDF and convert first page to image
        doc = fitz.open(filepath)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        image_path = os.path.join(app.config['IMAGE_FOLDER'], f"{os.path.splitext(filename)[0]}.png")
        pix.save(image_path)

        # SKIPPING OCR
        text = "(OCR temporarily disabled)"

        return render_template('result.html', text=text, image_url='/' + image_path)

    except Exception as e:
        return f"Error processing PDF: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
       
    
