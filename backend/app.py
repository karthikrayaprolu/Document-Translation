import os
import tempfile
import zipfile
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pdfplumber
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect
from functools import lru_cache

app = Flask(__name__)  # Initialize Flask app
CORS(app)  # Enable CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
TRANSLATIONS_FOLDER = os.path.join(BASE_DIR, 'translations')  
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PDF_TRANSLATIONS_FOLDER = os.path.join(TRANSLATIONS_FOLDER, 'pdfs')  
MODEL_FOLDER = os.path.join(BASE_DIR, 'models')

os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  
os.makedirs(TRANSLATIONS_FOLDER, exist_ok=True)  
os.makedirs(PDF_TRANSLATIONS_FOLDER, exist_ok=True)  

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    TRANSLATIONS_FOLDER=TRANSLATIONS_FOLDER,
    PDF_TRANSLATIONS_FOLDER=PDF_TRANSLATIONS_FOLDER
)

LANG_CODE_MAP = {  # Mapping source language codes to MarianMT model pairs
    'fr': 'fr-en', 'de': 'de-en', 'es': 'es-en', 'hi': 'hi-en',
    'zh-cn': 'zh-en', 'zh-tw': 'zh-en', 'ru': 'ru-en', 'ja': 'ja-en',
    'ko': 'ko-en', 'ar': 'ar-en', 'pt': 'pt-en', 'it': 'it-en',
    'nl': 'nl-en', 'sv': 'sv-en', 'pl': 'pl-en', 'tr': 'tr-en',
    'vi': 'vi-en', 'he': 'he-en', 'id': 'id-en', 'cs': 'cs-en',
    'ro': 'ro-en', 'da': 'da-en', 'fi': 'fi-en', 'hu': 'hu-en',
    'th': 'th-en'
}

@lru_cache(maxsize=10)
def get_model_and_tokenizer(src_lang_pair):
    """Load MarianMT model/tokenizer with local caching."""
    model_name = f"Helsinki-NLP/opus-mt-{src_lang_pair}"
    local_dir = os.path.join(BASE_DIR, 'models', f'opus-mt-{src_lang_pair}')
    os.makedirs(local_dir, exist_ok=True)

    if not os.path.exists(os.path.join(local_dir, 'pytorch_model.bin')):
        print(f"Downloading and caching model: {model_name}")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        tokenizer.save_pretrained(local_dir)
        model.save_pretrained(local_dir)
    else:
        print(f"Loading model from local path: {local_dir}")
        tokenizer = MarianTokenizer.from_pretrained(local_dir)
        model = MarianMTModel.from_pretrained(local_dir)

    return model, tokenizer


def detect_language(text):
    """Detect language; return 'en' if detection fails."""
    try:
        return detect(text).lower()
    except Exception:
        return "en"

def translate_text(text):
    """Translate text to English if needed; return original or error message."""
    if not text.strip():
        return ""
    detected_lang = detect_language(text)
    if detected_lang == 'en':
        return text
    lang_pair = LANG_CODE_MAP.get(detected_lang)
    if not lang_pair:
        return f"[Unsupported language: {detected_lang}] {text}"
    try:
        model, tokenizer = get_model_and_tokenizer(lang_pair)
        inputs = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        return f"[Translation Error] {str(e)}"

def clean_filename(filename):
    """Sanitize filename to prevent directory traversal."""
    return os.path.basename(filename)

def extract_data(text):
    """Extract key-value pairs from colon-separated lines."""
    lines = text.split('\n')
    data = []
    key, value = '', ''
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            if key:
                data.append((key.strip(), value.strip()))
            key, value = line.split(':', 1)
        else:
            value += f" {line}"
    if key:
        data.append((key.strip(), value.strip()))
    return data

def process_pdf(file_path):
    """Extract and combine text from all PDF pages."""
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return extract_data(text)

@app.route('/upload', methods=['POST'])
def upload_folder():
    """Handle multiple PDF uploads, translate and save Excel files."""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'error': 'No files selected'}), 400

    response_data = []
    all_data_rows = []

    for pdf_file in files:
        file_name = clean_filename(pdf_file.filename)
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            file_name = clean_filename(pdf_file.filename)
            saved_path = os.path.join(UPLOAD_FOLDER, file_name)
            pdf_file.save(saved_path)  

            pairs = process_pdf(saved_path)

            file_data = []
            for key, value in pairs:
                translated_key = translate_text(key)
                translated_value = translate_text(value)
                file_data.append({
                    "PDF Name": file_name,
                    "Original Key": key,
                    "Original Value": value,
                    "Translated Key": translated_key,
                    "Translated Value": translated_value
                })

            if file_data:
                df = pd.DataFrame(file_data)
                excel_name = f"{os.path.splitext(file_name)[0]}_translated.xlsx"
                excel_path = os.path.join(PDF_TRANSLATIONS_FOLDER, excel_name)
                df.to_excel(excel_path, index=False)

                all_data_rows.extend(file_data)
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
            temp.close()
            if os.path.exists(temp.name):
                os.unlink(temp.name)

    if all_data_rows:
        df_all = pd.DataFrame(all_data_rows)
        combined_excel_path = os.path.join(TRANSLATIONS_FOLDER, 'all_translations.xlsx')
        df_all.to_excel(combined_excel_path, index=False)

        metadata = {
            "files": [
                {"name": file["fileName"], "translatedFile": f"{os.path.splitext(file['fileName'])[0]}_translated.xlsx"}
                for file in response_data if file.get("status") == "translated"
            ]
        }
        metadata_path = os.path.join(TRANSLATIONS_FOLDER, 'translations_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

    return jsonify(response_data)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Serve individual or combined translation Excel files."""
    try:
        file_path = os.path.join(PDF_TRANSLATIONS_FOLDER, filename)
        if not os.path.exists(file_path):
            file_path = os.path.join(TRANSLATIONS_FOLDER, filename)
            if not os.path.exists(file_path):
                return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/download-all', methods=['GET'])
def download_all():
    """Zip all translation files and serve for download."""
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Start Flask app on port 5000
