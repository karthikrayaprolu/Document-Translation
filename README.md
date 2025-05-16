# Document Translation Application

A web-based application that translates PDF documents by extracting key-value pairs and provides translations in Excel format.

---

## 🚀 Features

- ✨ Upload multiple PDF files simultaneously  
- 📄 Extract key-value pairs from PDF documents  
- 🌐 Automatic translation to English using MarianMT models  
- 📊 Generate individual Excel reports per uploaded file  
- 📑 Create combined translation reports aggregating all files  
- 💾 Download individual translated Excel files or all files as a ZIP  
- 🗃️ Local caching of translation models to improve performance  
- 🔒 Secure filename handling and robust error handling  

---

## 🏗️ Project Structure

```

document-translation/
├── backend/
│ ├── app.py # Flask backend server
│ ├── uploads/ # Temporary PDF upload storage
│ ├── translations/ # Translation output folder
│ ├── pdfs/ # Individual translated Excel files
│ └── models/ # Cached MarianMT translation models
├── frontend/
│ ├── node_modules/ # Node.js dependencies
│ ├── src/
│ │ ├── components/ # React components
│ │ ├── hooks/ # Custom React hooks
│ │ ├── types/ # TypeScript type definitions
│ │ ├── utils/ # Utility functions
│ │ ├── App.tsx # Main React app component
│ │ ├── main.tsx # Entry point for React app
│ │ └── index.css # Global styles
│ ├── index.html # HTML template
│ ├── package.json # NPM dependencies and scripts
│ ├── vite.config.ts # Vite build config
│ ├── tsconfig.json # TypeScript config
│ ├── tailwind.config.js # Tailwind CSS config
│ ├── postcss.config.js # PostCSS config
│ └── eslint.config.js # ESLint config
├── README.md # Project overview and setup instructions
├── .gitignore # Git ignore rules
└── other-config-files/ # Other config files (optional)

````

---

## ⚙️ Installation

### Backend Setup

1. Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
````

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install required Python packages:

```bash
pip install flask flask-cors pdfplumber pandas openpyxl transformers langdetect
```

3. (Optional) If GPU acceleration is available and desired, install `torch` with CUDA support following [PyTorch's official instructions](https://pytorch.org/get-started/locally/).

---

### Frontend Setup

* Install dependencies using `npm install` or `yarn install`.
* Run the development server with `npm run dev` or `yarn dev`.
* The frontend will be available at `http://localhost:5173` (default Vite port).
* For production, build static files using `npm run build` or `yarn build`.
* Serve the built files from the `dist` folder using any static file server.
* Make sure the backend Flask server is running to handle API requests.

---

## 🚀 Running the Application

1. Start the Flask backend server:

```bash
cd backend
python app.py
```

2. Access the frontend by running the development server and opening http://localhost:5173 in your browser.

3. Upload PDF files for translation via frontend or send POST requests to `/upload` endpoint.

---

## 🛠️ API Endpoints

| Endpoint               | Method | Description                                 |
| ---------------------- | ------ | ------------------------------------------- |
| `/upload`              | POST   | Upload multiple PDF files for translation   |
| `/download/<filename>` | GET    | Download a specific translated Excel file   |
| `/download-all`        | GET    | Download all translation Excel files as ZIP |

---

## 💻 Usage Guide

1. Navigate to the frontend interface or use an API client.
2. Select or drag & drop one or more PDF files for upload.
3. Click "Upload" to start processing.
4. Wait while the server extracts text, detects language, translates keys/values to English, and generates Excel files.
5. Download individual translation Excel files or all files zipped together.

---

## 🔧 Technologies Used

### Backend

* Python 3.x
* Flask
* Flask-CORS
* pdfplumber (PDF text extraction)
* pandas (data handling and Excel export)
* openpyxl (Excel file writing)
* Hugging Face Transformers (MarianMT translation models)
* langdetect (automatic language detection)

### Frontend

* React with TypeScript
* HTML5
* CSS3 (including Tailwind CSS)
* JavaScript (ES6+)
* Vite (build tool and dev server)
* PostCSS (for CSS processing)
* ESLint (for code linting)

---

## 📝 Implementation Details & Notes

* The backend caches MarianMT models locally under `backend/models/` to reduce repeated downloads and improve response time.
* The language detector detects source language of PDF extracted text; if English, no translation is done.
* Supports translations from 24+ source languages to English (see `LANG_CODE_MAP` in backend).
* Uploaded PDFs are temporarily stored in `uploads/` and individual translated Excel files saved in `translations/pdfs/`.
* A combined Excel report aggregating all files is saved as `translations/all_translations.xlsx`.
* File download endpoints serve files securely and respond with errors if files are missing.
* The `/download-all` endpoint packages all translated Excels and the combined Excel into a ZIP for bulk download.
* Filenames are sanitized to prevent directory traversal vulnerabilities.
* Error handling is implemented for file processing, translation failures, and download requests.
* Temporary files are cleaned up after use.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m "Add AmazingFeature"`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## Contact

For questions or support, please open an issue or contact the maintainer.
