from flask import Flask, render_template_string, request, redirect
import os
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

# Configure Tesseract path (update if installed somewhere else)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configure Poppler path
POPPLER_PATH = r"C:\Users\User\Documents\Poppler-24.08.0\Library\bin"

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template_string('''
        <h2>Upload a PDF</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf">
            <input type="submit" value="Upload">
        </form>
    ''')

@app.route('/upload', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'GET':
        return redirect('/')
    
    if 'pdf' not in request.files:
        return 'No file uploaded.', 400

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return 'No file selected.', 400

    file_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)
    pdf_file.save(file_path)

    try:
        pages = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        output_image_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
        pages[0].save(output_image_path, 'JPEG')

        extracted_text = pytesseract.image_to_string(Image.open(output_image_path))
        return f"<h2>Extracted Text:</h2><pre>{extracted_text}</pre>"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)