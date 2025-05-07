import React from 'react';
import { FileUp as FileUpload, Upload, FolderUp } from 'lucide-react';

interface FileUploadAreaProps {
  isDragging: boolean;
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragLeave: (e: React.DragEvent<HTMLDivElement>) => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const FileUploadArea: React.FC<FileUploadAreaProps> = ({
  isDragging,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect
}) => {
  return (
    <div
      className={`flex-1 flex items-center justify-center p-6 transition-all duration-300 ${
        isDragging ? 'bg-blue-100/10 border-blue-400/30' : ''
      }`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <div className="flex flex-col items-center space-y-6">
        <input
          type="file"
          multiple
          onChange={onFileSelect}
          className="hidden"
          id="file-upload"
        />
        <input
          type="file"
          ref={(input) => {
            if (input) {
              input.setAttribute('webkitdirectory', '');
              input.setAttribute('directory', '');
            }
          }}
          onChange={onFileSelect}
          className="hidden"
          id="folder-upload"
        />
        
        <div className="flex space-x-4">
          <label
            htmlFor="file-upload"
            className="cursor-pointer"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-10 flex flex-col items-center justify-center transition-all duration-300 hover:border-blue-400/30 hover:bg-blue-100/5">
              <div className="p-6 mb-6 rounded-full bg-blue-500/10 text-blue-400">
                <FileUpload size={40} className="animate-pulse" />
              </div>
              <p className="text-gray-200 text-xl mb-6 text-center">
                Upload Files
              </p>
              <button className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg transition-all shadow-lg shadow-blue-500/20 font-medium flex items-center">
                <Upload size={18} className="mr-2" />
                Select Files
              </button>
            </div>
          </label>

          <label
            htmlFor="folder-upload"
            className="cursor-pointer"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-10 flex flex-col items-center justify-center transition-all duration-300 hover:border-blue-400/30 hover:bg-blue-100/5">
              <div className="p-6 mb-6 rounded-full bg-blue-500/10 text-blue-400">
                <FolderUp size={40} className="animate-pulse" />
              </div>
              <p className="text-gray-200 text-xl mb-6 text-center">
                Upload Folder
              </p>
              <button className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg transition-all shadow-lg shadow-blue-500/20 font-medium flex items-center">
                <FolderUp size={18} className="mr-2" />
                Select Folder
              </button>
            </div>
          </label>
        </div>

        <p className="text-gray-400 text-sm">
          Supported file types: Documents, PDFs, Images
        </p>
      </div>
    </div>
  );
};

export default FileUploadArea;