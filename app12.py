from flask import Flask, request, render_template, redirect, url_for
from pdf2image import convert_from_path
import os

# Create Flask app
app = Flask(__name__)

# Create folders if they don't exist
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set upload folder in config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home page with upload form
@app.route('/')
def index():
    return '''
        <h2>Upload a PDF</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
    '''

# Upload route
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
            # Convert PDF to image using Poppler
            images = convert_from_path(
                filepath,
                poppler_path=r'C:\Users\User\Document\Poppler-24.08.0\Library\bin'
            )

            # Save first page as JPEG
            output_path = os.path.join(OUTPUT_FOLDER, 'page1.jpg')
            images[0].save(output_path, 'JPEG')

            return f"PDF processed successfully. First page saved as <code>{output_path}</code>"

        except Exception as e:
            return f"Error extracting text: {e}"

    return redirect(url_for('index'))

# Run app
if __name__ == '__main__':
    app.run(debug=True)