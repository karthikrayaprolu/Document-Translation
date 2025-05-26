# Import necessary libraries
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import pdfplumber
import pandas as pd
import json
import torch
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Define and create required directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TRANSLATIONS_FOLDER = os.path.join(BASE_DIR, 'translations')
PDF_TRANSLATIONS_FOLDER = os.path.join(TRANSLATIONS_FOLDER, 'pdfs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATIONS_FOLDER, exist_ok=True)
os.makedirs(PDF_TRANSLATIONS_FOLDER, exist_ok=True)

# Configure folders for Flask app
app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    TRANSLATIONS_FOLDER=TRANSLATIONS_FOLDER,
    PDF_TRANSLATIONS_FOLDER=PDF_TRANSLATIONS_FOLDER
)

# Set computation device for translation model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model cache to avoid reloading the same model
model_cache = {}

# Define supported language code mappings to English
language_code_map = {
    'de': 'de-en', 'fr': 'fr-en', 'es': 'es-en', 'ru': 'ru-en', 'it': 'it-en',
    'nl': 'nl-en', 'pl': 'pl-en', 'pt': 'pt-en', 'ro': 'ro-en', 'cs': 'cs-en',
    'bg': 'bg-en', 'sk': 'sk-en', 'sv': 'sv-en', 'hu': 'hu-en', 'el': 'tc-big-el-en',
    'fi': 'fi-en', 'uk': 'uk-en', 'lt': 'lt-en', 'lv': 'lv-en', 'et': 'et-en',
    'hi': 'hi-en', 'zh': 'zh-en', 'ja': 'ja-en', 'ko': 'ko-en', 'ar': 'ar-en',
    'tr': 'tr-en', 'vi': 'vi-en', 'he': 'he-en', 'id': 'id-en', 'da': 'da-en',
    'th': 'th-en', 'no': 'no-en'
}

# Remove any unwanted characters from filename
def clean_filename(filename):
    return os.path.basename(filename)

# Extract key-value pairs from given text using ':' separator
def extractData(text):
    lines = text.split('\n')
    data = []
    key, value = '', ''
    for line in lines:
        if ':' in line:
            if key:
                data.append((key.strip(), value.strip()))
            parts = line.split(':', 1)
            key = parts[0]
            value = parts[1]
        else:
            value += f"\n{line}"
    if key:
        data.append((key.strip(), value.strip()))
    return data

# Extract text from a PDF file using pdfplumber
def processPdf(filePath):
    with pdfplumber.open(filePath) as pdf:
        text = ''
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + '\n'
    return extractData(text)

# Load translation model for a specific language pair
def load_model(lang_pair):
    model_name = f"Helsinki-NLP/opus-mt-{lang_pair}"
    if model_name not in model_cache:
        print(f"Loading model: {model_name}")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name).to(device)
        model_cache[model_name] = (tokenizer, model)
    return model_cache[model_name]

# Batch translate a list of strings
def batchTranslate(texts, model_name):
    tokenizer, model = model_cache[model_name]
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs)
    return [tokenizer.decode(t, skip_special_tokens=True) for t in outputs]

# Detect language and get language pair
def detect_language_and_model(text):
    try:
        src_lang = detect(text)
        lang_pair = language_code_map.get(src_lang)
        return lang_pair
    except:
        return None

# Upload and translate multiple PDF files
@app.route('/upload', methods=['POST'])
def uploadFolder():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No selected files'}), 400

    response_data = []
    all_data_rows = []
    metadata_files = []

    for pdf in files:
        file_name = clean_filename(pdf.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, file_name)
        pdf.save(upload_path)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            with open(upload_path, 'rb') as f_in:
                temp.write(f_in.read())

            pairs = processPdf(temp.name)

            if not pairs:
                continue

            # Combine all values to detect source language
            combined_text = " ".join([val for _, val in pairs])
            lang_pair = detect_language_and_model(combined_text)

            if not lang_pair:
                response_data.append({
                    "fileName": file_name,
                    "status": "error",
                    "error": "Unsupported or undetectable language"
                })
                continue

            load_model(lang_pair)

            # Batch translate keys and values
            keys = [key for key, _ in pairs]
            values = [val for _, val in pairs]
            translated_keys = batchTranslate(keys, f"Helsinki-NLP/opus-mt-{lang_pair}")
            translated_values = batchTranslate(values, f"Helsinki-NLP/opus-mt-{lang_pair}")

            file_data = []
            suspicious_translations = 0
            confidence_scores = []

            for i in range(len(pairs)):
                key, value = pairs[i]
                t_key = translated_keys[i]
                t_val = translated_values[i]

                confidence = len(t_val.strip()) / max(len(value.strip()), 1)
                confidence = round(min(max(confidence, 0), 1), 2)
                confidence_scores.append(confidence)

                if len(t_val.strip()) < 2:
                    suspicious_translations += 1

                file_data.append({
                    "PDF Name": file_name,
                    "Original Key": key,
                    "Original Value": value,
                    "Translated Key": t_key,
                    "Translated Value": t_val
                })

            df = pd.DataFrame(file_data)
            excel_name = f"{os.path.splitext(file_name)[0]}_translated.xlsx"
            excel_path = os.path.join(PDF_TRANSLATIONS_FOLDER, excel_name)
            df.to_excel(excel_path, index=False)
            all_data_rows.extend(file_data)

            stats = {
                "fileName": file_name,
                "totalPairs": len(pairs),
                "translationErrors": 0,
                "suspiciousTranslations": suspicious_translations,
                "averageConfidence": round(sum(confidence_scores)/len(confidence_scores), 2),
                "status": "translated",
                "translatedFile": excel_name
            }
            metadata_files.append(stats)

            response_data.append({
                "fileName": file_name,
                "status": stats["status"],
                "translatedFile": excel_name
            })

        except Exception as e:
            response_data.append({
                "fileName": file_name,
                "status": "error",
                "error": str(e)
            })
        finally:
            temp.close()
            if os.path.exists(temp.name):
                os.unlink(temp.name)

    if all_data_rows:
        df_all = pd.DataFrame(all_data_rows)
        combined_path = os.path.join(TRANSLATIONS_FOLDER, 'all_translations.xlsx')
        df_all.to_excel(combined_path, index=False)

    if metadata_files:
        metadata_path = os.path.join(TRANSLATIONS_FOLDER, 'translations_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump({"files": metadata_files}, f, indent=2)

    return jsonify(response_data)

# Download specific translated Excel file by name
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(PDF_TRANSLATIONS_FOLDER, filename)
        if not os.path.exists(file_path):
            file_path = os.path.join(TRANSLATIONS_FOLDER, filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Download all translated Excel files as a ZIP archive
@app.route('/download-all', methods=['GET'])
def download_all():
    try:
        zip_filename = "all_translations.zip"
        zip_path = os.path.join(TRANSLATIONS_FOLDER, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(PDF_TRANSLATIONS_FOLDER):
                if file.endswith('.xlsx'):
                    file_path = os.path.join(PDF_TRANSLATIONS_FOLDER, file)
                    zipf.write(file_path, os.path.join('individual_translations', file))

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

# Run the Flask application on localhost
if __name__ == '__main__':
    app.run(debug=True, port=5000)
