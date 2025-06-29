import os
from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
import fitz # PyMuPDF

UPLOAD_FOLDER = 'uploads'
STAMPED_FOLDER = 'static/stamped'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STAMPED_FOLDER'] = STAMPED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STAMPED_FOLDER, exist_ok=True)

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
        # Open and stamp the PDF
        doc = fitz.open(filepath)
        page = doc[0]
        width, height = page.rect.width, page.rect.height

        # Stamp settings
        font_size = 20
        box_width = 300
        box_height = 80
        box_x = (width - box_width) / 2
        box_y = (height - box_height) / 2
        box_rect = fitz.Rect(box_x, box_y, box_x + box_width, box_y + box_height)

        # Draw bold black rectangle (box)
        page.draw_rect(box_rect, color=(0, 0, 0), width=2)

        # Insert bold black text inside the box
        page.insert_textbox(
            box_rect,
            "CERTIFIED BY EAZY SERT",
            fontsize=font_size,
            fontname="helv",
            color=(0, 0, 0),
            render_mode=3, # bold stroke text
            align=1 # center
        )

        stamped_filename = f"stamped_{filename}"
        stamped_path = os.path.join(app.config['STAMPED_FOLDER'], stamped_filename)
        doc.save(stamped_path)
        doc.close()

        return render_template('result.html', stamped_file=stamped_filename)

    except Exception as e:
        return f"Error processing PDF: {str(e)}"

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['STAMPED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
    

        
        
