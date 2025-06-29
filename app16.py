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
        doc = fitz.open(filepath)
        page = doc[0]
        width, height = page.rect.width, page.rect.height

        # Rectangle dimensions and position
        box_width, box_height = 300, 100
        center_x, center_y = width / 2, height / 2
        rect = fitz.Rect(center_x - box_width / 2, center_y - box_height / 2,
                         center_x + box_width / 2, center_y + box_height / 2)

        # Draw bold box
        shape = page.new_shape()
        shape.draw_rect(rect)
        shape.finish(width=2, color=(0, 0, 0))
        shape.commit()

        # Insert bold black text in the center of the box
        stamp_text = "CERTIFIED BY EAZY SERT"
        font_size = 22 # should fit well
        page.insert_textbox(
            rect,
            stamp_text,
            fontsize=font_size,
            fontname="helv",
            color=(0, 0, 0), # black
            render_mode=3, # bold
            align=1 # center
        )

        # Save stamped file
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

   
        

        
   

