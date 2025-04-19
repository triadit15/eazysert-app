from flask import Flask, request, redirect, url_for
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
import traceback

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set the path to tesseract.exe (update if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/')
def index():
    return '''
        <h2>Upload a PDF</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            images = convert_from_path(
                filepath,
                poppler_path=r'C:\Users\User\Documents\Poppler-24.08.0\Library\bin'
            )

            output_image_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
            images[0].save(output_image_path, 'JPEG')

            # OCR the image
            extracted_text = pytesseract.image_to_string(Image.open(output_image_path))

            return f"""
                <h3>PDF processed successfully!</h3>
                <p>First page saved as: <code>{output_image_path}</code></p>
                <h4>Extracted Text:</h4>
                <pre>{extracted_text}</pre>
            """

        except Exception as e:
            error_msg = traceback.format_exc()
            return f"Error:<br><pre>{error_msg}</pre>"

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)