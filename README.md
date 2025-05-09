# Document Translation Application

A web-based application that translates PDF documents, extracts key-value pairs, and provides translations in Excel format.

## 🚀 Features

- ✨ Upload multiple PDF files simultaneously
- 📄 Extract key-value pairs from PDF documents
- 🌐 Automatic translation to English
- 📊 Generate individual Excel reports per file
- 📑 Create combined translation reports
- 💾 Download individual or bulk translations
- 🗃️ ZIP file support for bulk downloads

## 🏗️ Project Structure

```
document-translation/
├── backend/
│   ├── new.py              # Flask server
│   ├── uploads/            # Temporary PDF storage
│   └── translations/       # Translation output
│       └── pdfs/          # Individual translations
└── frontend/
    ├── index.html         # Main application page
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## ⚙️ Installation

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install flask flask-cors googletrans==3.1.0a0 pdfplumber pandas openpyxl
```

### Frontend Setup

No installation required - just serve the static files using any web server.

## 🚀 Running the Application

1. Start the Flask server:
```bash
cd backend
python new.py
```

2. Access the application:
   - Backend runs at: `http://localhost:5000`
   - Open `frontend/index.html` in your browser

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload PDF files for translation |
| `/download/<filename>` | GET | Download specific translation |
| `/download-all` | GET | Download all translations as ZIP |

## 💻 Usage Guide

1. Open the web interface
2. Click "Choose Files" or drag & drop PDFs
3. Click "Upload" to start translation
4. Wait for processing completion
5. Download translations individually or as ZIP

## 🔧 Technologies Used

- **Backend**
  - Python 3.x
  - Flask
  - googletrans
  - pdfplumber
  - pandas

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript (ES6+)

## 📝 Notes

- Supports multiple PDF uploads
- Automatically creates required directories
- Temporary files are stored in `uploads/` and `translations/`
- All translations are converted to English

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.