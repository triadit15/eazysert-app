from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import os

# Configure app
app = Flask(__name__)
app.secret_key = 'secret123'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\path\to\poppler\bin' # <<< UPDATE this to your actual Poppler path

# Check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract text function
def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    if ext == ".pdf":
        images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
        for img in images:
            text += pytesseract.image_to_string(img)
    else:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
    return text

# Routes
@app.route('/')
def index():
    return redirect(url_for('upload_file'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                extracted_text = extract_text(filepath)
                return render_template('upload.html', text=extracted_text)
            except Exception as e:
                return f"Error extracting text: {e}"
        else:
            flash('Invalid file type.')
            return redirect(request.url)

    return render_template('upload.html', text="")

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)