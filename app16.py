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

        # Rectangle specs
        box_width = 300
        box_height = 100
        center_x = width / 2
        center_y = height / 2

        rect = fitz.Rect(center_x - box_width / 2, center_y - box_height / 2,
                         center_x + box_width / 2, center_y + box_height / 2)

        # Draw bold box
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(width=2, color=(0, 0, 0)) # thick black
        shape.commit()

        stamp_text = "CERTIFIED BY EAZY SERT"
        max_font_size = 30
        min_font_size = 10
        fitted_font = min_font_size

        # Try font sizes from large to small until it fits
        for font_size in range(max_font_size, min_font_size - 1, -1):
            text_width = fitz.get_text_length(stamp_text, fontname="helv", fontsize=font_size)
            if text_width <= box_width - 10: # padding
                fitted_font = font_size
                break

        # Insert text inside the box
        page.insert_textbox(
            rect,
            stamp_text,
            fontsize=fitted_font,
            fontname="helv",
            color=(0, 0, 0),
            render_mode=3, # bold
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
    
       
            


