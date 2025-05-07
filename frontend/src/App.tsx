import React from 'react';
import Header from './components/Header';
import FileUploadArea from './components/FileUploadArea';
import FileList from './components/FileList';
import ActionButtons from './components/ActionButtons';
import { useFileUpload } from './hooks/useFileUpload';
import { useTranslation } from './hooks/useTranslation';
import { downloadFile, downloadAllFiles } from './utils/fileUtils';

interface File {
  id: string;
  name: string;
  status: 'pending' | 'translating' | 'translated' | 'error';
  // Add other file properties as needed
}

function App() {
  const {
    files,
    setFiles,
    isDragging,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    removeFile
  } = useFileUpload();

  const { isTranslating, handleSubmitForTranslation } = useTranslation(files, setFiles);

  const hasTranslatedFiles = files.some((file: File) => file.status === 'translated');

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex flex-col">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-transparent to-transparent"></div>
        <div className="absolute top-0 w-full h-64 bg-gradient-to-b from-blue-900/20 to-transparent"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col max-w-5xl w-full mx-auto px-4">
        <Header />
        
        <div className="flex-1 flex flex-col">
          <FileUploadArea
            isDragging={isDragging}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onFileSelect={handleFileSelect}
          />
          
          {files.length > 0 && (
            <div className="mt-8 mb-4">
              <FileList 
                files={files} 
                onDownload={downloadFile}
                onRemove={removeFile}
              />
            </div>
          )}
        </div>

        <ActionButtons
          onTranslate={handleSubmitForTranslation}
          onDownloadAll={() => downloadAllFiles(files)}
          isTranslating={isTranslating}
          hasFiles={files.length > 0}
          hasTranslatedFiles={hasTranslatedFiles}
        />
      </div>

      {/* Footer */}
      <footer className="relative z-10 p-4 text-center text-gray-500 text-sm">
        <p>© 2025 Document Translation Service. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;