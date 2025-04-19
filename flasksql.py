from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from flask_sqlalchemy import SQLAlchemy

# App config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certifications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# External tool paths
POPPLER_PATH = r'C:\Users\User\Documents\poppler-24.08.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize DB
db = SQLAlchemy(app)

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# DB model
class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    id_number = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    extracted_text = db.Column(db.Text)
    image_path = db.Column(db.String(200))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['pdf']
        id_number = request.form['id_number']
        full_name = request.form['full_name']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Convert PDF to image
            try:
                images = convert_from_path(filepath, poppler_path=POPPLER_PATH, first_page=1, last_page=1)
                image = images[0]
                output_image_path = os.path.join(app.config['OUTPUT_FOLDER'], 'page1.jpg')
                image.save(output_image_path)
            except Exception as e:
                return f"Error converting PDF: {e}"

            # Extract text
            try:
                extracted_text = pytesseract.image_to_string(Image.open(output_image_path))
            except Exception as e:
                return f"Error extracting text: {e}"

            # Simulated identity verification
            verified = id_number == "0202155519087" and full_name.strip().lower() == "siyabonga shipalana"

            # Add certification stamp
            try:
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("arial.ttf", 24)
                draw.text((30, 30), "Certified by Eazy Sert", fill=(255, 0, 0), font=font)
                image.save(output_image_path)
            except Exception as e:
                return f"Error adding stamp: {e}"

            # Save to database
            cert = Certification(
                full_name=full_name,
                id_number=id_number,
                extracted_text=extracted_text,
                image_path='page1.jpg'
            )
            db.session.add(cert)
            db.session.commit()

            result = "Verified and Certified" if verified else "Verification Failed"
            return render_template("verify_result.html", result=result, image_path='page1.jpg')

    return render_template("i
ndex.html")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

# Ensure DB is ready
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)