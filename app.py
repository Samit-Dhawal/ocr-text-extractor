import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pytesseract
from pdf2image import convert_from_path
import cv2

# File configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png','tiff','svg','bmp','eps', 'pdf','heic','odt','psd'}

app = Flask(__name__)

# Ensuring the 'uploads' directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'samit123'

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Function to convert PDF to image
def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(app.config['UPLOAD_FOLDER'],f'page_{i}.png')
        image.save(image_path)
        image_paths.append(image_path)
    return image_paths

# Function to extract text from image
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    extracted_text = pytesseract.image_to_string(gray)
    return extracted_text

# Function to delete uploaded files
def delete_uploaded_files(file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {file_path}, Error: {e}")

# Text extraction route
@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Checking if the file is a PDF and converting it to an image
        if filename.endswith('.pdf'):
            pdf_path = file_path
            image_paths = convert_pdf_to_image(pdf_path)
            extracted_text = ""
            for image_path in image_paths:
                extracted_text += extract_text_from_image(image_path) + "\n"
            # Deleting temporary image files
            delete_uploaded_files(image_paths)
        else:
            image_path = file_path
            extracted_text = extract_text_from_image(image_path)
        
        # Deleting the uploaded file
        delete_uploaded_files([file_path])

        return render_template('index.html', extracted_text=extracted_text)
    else:
        flash('Invalid file format. Allowed formats are jpg, jpeg, png, and pdf')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
