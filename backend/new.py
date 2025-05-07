import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from googletrans import Translator
import os
import tempfile
import pdfplumber
import pandas as pd
import json

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define base directory and ensure absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TRANSLATIONS_FOLDER = os.path.join(BASE_DIR, 'translations')
PDF_TRANSLATIONS_FOLDER = os.path.join(TRANSLATIONS_FOLDER, 'pdfs')

# Create all required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATIONS_FOLDER, exist_ok=True)
os.makedirs(PDF_TRANSLATIONS_FOLDER, exist_ok=True)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    TRANSLATIONS_FOLDER=TRANSLATIONS_FOLDER,
    PDF_TRANSLATIONS_FOLDER=PDF_TRANSLATIONS_FOLDER
)

# Initialize the Google Translator
translator = Translator()

# Function to ensure filename is safe and consistent
def clean_filename(filename):
    return os.path.basename(filename)

# Function to extract key-value pairs from text
def extractData(text):
    lines = text.split('\n')
    data = []
    key, value = '', ''
    for line in lines:
        if ':' in line:  # If a colon is found, assume it's a key-value pair
            if key:  # If a key already exists, save the previous pair
                data.append((key.strip(), value.strip()))
            parts = line.split(':', 1)  # Split the line into key and value
            key = parts[0]
            value = parts[1]
        else:
            value += f"\n{line}"  # Add lines to the value if they don't have a colon
    if key:
        data.append((key.strip(), value.strip()))  # Append the last key-value pair
    return data

# Function to process a PDF file and extract text
def processPdf(filePath):
    with pdfplumber.open(filePath) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'  # Extract text from all pages of the PDF
    return extractData(text)  # Extract key-value pairs from the text

# Function to translate text into English
def translateText(text):
    if not text.strip():  # If text is empty or contains only spaces, return an empty string
        return ""
    try:
        translated = translator.translate(text, dest='en')  # Translate to English
        return translated.text
    except Exception as e:  # Catch any translation errors
        return f"[Translation Error] {str(e)}"

# Endpoint to upload multiple PDFs and process them
@app.route('/upload', methods=['POST'])
def uploadFolder():
    if 'files[]' not in request.files:  # Check if there is a 'files[]' field in the request
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')  # Get the list of uploaded files
    if not files:  # If no files are uploaded, return an error
        return jsonify({'error': 'No selected files'}), 400

    response_data = []  # List to store response data for each file
    all_data_rows = []  # List to store all extracted data

    for pdf in files:
        file_name = clean_filename(pdf.filename)  # Ensure filename is safe
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")  # Create a temporary file for the PDF
        try:
            pdf.save(temp.name)  # Save the uploaded PDF to the temporary file
            pairs = processPdf(temp.name)  # Process the PDF and extract key-value pairs
            file_data = []  # List to store the extracted data for this file
            
            for key, value in pairs:
                # Translate both key and value and store them in file_data
                translated_key = translateText(key)
                translated_value = translateText(value)
                file_data.append({
                    "PDF Name": file_name,
                    "Original Key": key,
                    "Original Value": value,
                    "Translated Key": translated_key,
                    "Translated Value": translated_value
                })
            
            # Save individual file translation
            if file_data:
                df = pd.DataFrame(file_data)
                excel_name = f"{os.path.splitext(file_name)[0]}_translated.xlsx"
                excel_path = os.path.join(PDF_TRANSLATIONS_FOLDER, excel_name)
                df.to_excel(excel_path, index=False)
                
                all_data_rows.extend(file_data)  # Add the file data to the overall data
                response_data.append({
                    "fileName": file_name,
                    "status": "translated",
                    "translatedFile": excel_name
                })
            
        except Exception as e:
            response_data.append({
                "fileName": file_name,
                "status": "error",
                "error": str(e)
            })
        finally:
            temp.close()  # Close the temporary file
            if os.path.exists(temp.name):
                os.unlink(temp.name)  # Delete the temporary file

    # Save combined translations if we have data
    if all_data_rows:
        df_all = pd.DataFrame(all_data_rows)
        combined_excel_path = os.path.join(TRANSLATIONS_FOLDER, 'all_translations.xlsx')
        df_all.to_excel(combined_excel_path, index=False)

        # Save translation metadata
        metadata = {
            "files": [
                {"name": file["fileName"], "translatedFile": f"{os.path.splitext(file['fileName'])[0]}_translated.xlsx"}
                for file in response_data if file["status"] == "translated"
            ]
        }
        metadata_path = os.path.join(TRANSLATIONS_FOLDER, 'translations_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

    return jsonify(response_data)

# Endpoint to download a specific file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # First try to find the file in the PDF translations folder
        file_path = os.path.join(PDF_TRANSLATIONS_FOLDER, filename)
        if not os.path.exists(file_path):
            # If not found, try the main translations folder
            file_path = os.path.join(TRANSLATIONS_FOLDER, filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Endpoint to download all translated files as a zip
@app.route('/download-all', methods=['GET'])
def download_all():
    try:
        zip_filename = "all_translations.zip"
        zip_path = os.path.join(TRANSLATIONS_FOLDER, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add files from PDF translations folder
            for file in os.listdir(PDF_TRANSLATIONS_FOLDER):
                if file.endswith('.xlsx'):
                    file_path = os.path.join(PDF_TRANSLATIONS_FOLDER, file)
                    zipf.write(file_path, os.path.join('individual_translations', file))
            
            # Add combined translations file
            combined_path = os.path.join(TRANSLATIONS_FOLDER, 'all_translations.xlsx')
            if os.path.exists(combined_path):
                zipf.write(combined_path, 'all_translations.xlsx')
        
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='translated_documents.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)