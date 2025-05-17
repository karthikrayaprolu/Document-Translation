import os
import tempfile
import zipfile
import json
import urllib.request
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pdfplumber
import pandas as pd
from transformers import MarianMTModel, MarianTokenizer
from functools import lru_cache
import fasttext

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TRANSLATIONS_FOLDER = os.path.join(BASE_DIR, 'translations')
PDF_TRANSLATIONS_FOLDER = os.path.join(TRANSLATIONS_FOLDER, 'pdfs')
MODEL_FOLDER = os.path.join(BASE_DIR, 'models')
METADATA_FOLDER = os.path.join(TRANSLATIONS_FOLDER, 'metadata')
FASTTEXT_MODEL_PATH = os.path.join(MODEL_FOLDER, 'lid.176.bin')
FASTTEXT_MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSLATIONS_FOLDER, exist_ok=True)
os.makedirs(PDF_TRANSLATIONS_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    TRANSLATIONS_FOLDER=TRANSLATIONS_FOLDER,
    PDF_TRANSLATIONS_FOLDER=PDF_TRANSLATIONS_FOLDER
)

# Download FastText model if not available
if not os.path.exists(FASTTEXT_MODEL_PATH):
    print("Downloading FastText language identification model...")
    urllib.request.urlretrieve(FASTTEXT_MODEL_URL, FASTTEXT_MODEL_PATH)
    print("FastText model downloaded successfully.")

# Load FastText model
fasttext_lang_model = fasttext.load_model(FASTTEXT_MODEL_PATH)

# Map of language codes to MarianMT model pairs
LANG_CODE_MAP = {
    'fr': 'fr-en', 'de': 'de-en', 'es': 'es-en', 'hi': 'hi-en',
    'zh': 'zh-en', 'ru': 'ru-en', 'ja': 'ja-en', 'ko': 'ko-en',
    'ar': 'ar-en', 'pt': 'pt-en', 'it': 'it-en', 'nl': 'nl-en',
    'sv': 'sv-en', 'pl': 'pl-en', 'tr': 'tr-en', 'vi': 'vi-en',
    'he': 'he-en', 'id': 'id-en', 'cs': 'cs-en', 'ro': 'ro-en',
    'da': 'da-en', 'fi': 'fi-en', 'hu': 'hu-en', 'th': 'th-en',
    'no': 'no-en', 'sw': 'sw-en'
}

@lru_cache(maxsize=10)
def get_model_and_tokenizer(src_lang_pair):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang_pair}"
    local_dir = os.path.join(MODEL_FOLDER, f'opus-mt-{src_lang_pair}')
    os.makedirs(local_dir, exist_ok=True)

    if not os.path.exists(os.path.join(local_dir, 'pytorch_model.bin')):
        print(f"Downloading and caching MarianMT model: {model_name}")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        tokenizer.save_pretrained(local_dir)
        model.save_pretrained(local_dir)
    else:
        tokenizer = MarianTokenizer.from_pretrained(local_dir)
        model = MarianMTModel.from_pretrained(local_dir)

    return model, tokenizer

def detect_language(text):
    """Use FastText to detect the language."""
    try:
        prediction = fasttext_lang_model.predict(text.strip().replace('\n', ' '), k=1)
        lang_code = prediction[0][0].replace('__label__', '').lower()
        return lang_code
    except Exception:
        return "en"

def translate_text(text):
    """Translate non-English text to English using MarianMT."""
    if not text.strip():
        return ""
    detected_lang = detect_language(text)
    if detected_lang == 'en':
        return text
    lang_pair = LANG_CODE_MAP.get(detected_lang)
    if not lang_pair:
        return f"[No translation model available for detected language '{detected_lang}'] {text}"
    try:
        model, tokenizer = get_model_and_tokenizer(lang_pair)
        inputs = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
        translated = model.generate(**inputs)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except Exception as e:
        return f"[Translation Error] {str(e)}"

def clean_filename(filename):
    return os.path.basename(filename)

def extract_data(text):
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
    with pdfplumber.open(file_path) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return extract_data(text)

@app.route('/upload', methods=['POST'])
def upload_folder():
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
            saved_path = os.path.join(UPLOAD_FOLDER, file_name)
            pdf_file.save(saved_path)
            pairs = process_pdf(saved_path)
            file_data = []

            # 🔽 Stats tracking variables
            translation_errors = 0
            suspicious_translations = 0
            total_pairs = 0
            fasttext_confidences = []

            for key, value in pairs:
                total_pairs += 1

                # Detect language with confidence
                text_for_detection = (key + " " + value).strip()
                prediction = fasttext_lang_model.predict(text_for_detection, k=1)
                lang_code = prediction[0][0].replace('__label__', '').lower()
                confidence = prediction[1][0]
                fasttext_confidences.append(confidence)

                translated_key = translate_text(key)
                translated_value = translate_text(value)

                if translated_key.startswith("[Translation Error]") or translated_value.startswith("[Translation Error]"):
                    translation_errors += 1
                if lang_code != 'en' and (translated_key == key or translated_value == value):
                    suspicious_translations += 1

                file_data.append({
                    "PDF Name": file_name,
                    "Original Key": key,
                    "Original Value": value,
                    "Translated Key": translated_key,
                    "Translated Value": translated_value
                })

            # 🔽 Generate stats here 
            avg_confidence = sum(fasttext_confidences) / len(fasttext_confidences) if fasttext_confidences else 0
            excel_name = f"{os.path.splitext(file_name)[0]}_translated.xlsx"
            stats = {
                "fileName": file_name,
                "totalPairs": total_pairs,
                "translationErrors": translation_errors,
                "suspiciousTranslations": suspicious_translations,
                "avgFastTextConfidence": avg_confidence,
                "status": "translated" if translation_errors == 0 else "partial_errors",
                "translatedFile": excel_name if file_data else None
            }
            response_data.append(stats)

            # 🔽 Save Excel and extend data
            if file_data:
                df = pd.DataFrame(file_data)
                excel_path = os.path.join(PDF_TRANSLATIONS_FOLDER, excel_name)
                df.to_excel(excel_path, index=False)
                all_data_rows.extend(file_data)

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

    # Save combined Excel and metadata.json separately in a folder
    if all_data_rows:
        df_all = pd.DataFrame(all_data_rows)
        combined_excel_path = os.path.join(TRANSLATIONS_FOLDER, 'all_translations.xlsx')
        df_all.to_excel(combined_excel_path, index=False)

        metadata_path = os.path.join(METADATA_FOLDER, 'translations_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(response_data, f)

    return jsonify(response_data)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
