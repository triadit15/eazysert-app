from flask import Flask, render_template, request, redirect, url_for
import fitz # PyMuPDF
import pytesseract
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return 'No file part'

    file = request.files['pdf']
    if file.filename == '':
        return 'No selected file'

    if file:
        # Save uploaded PDF
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        # Convert first page to image using PyMuPDF
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0) # Load the first page
            pix = page.get_pixmap()
            image_path = os.path.join(STATIC_FOLDER, 'output.png')
            pix.save(image_path)

            # OCR the image using Tesseract
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

            return render_template('result.html', text=text, image_url='/' + image_path)
        except Exception as e:
            return f"Error processing PDF: {e}"

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
