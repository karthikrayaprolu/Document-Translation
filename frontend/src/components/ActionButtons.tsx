import React from 'react';
import { FileText, Download } from 'lucide-react';

interface ActionButtonsProps {
  onTranslate: () => void;
  onDownloadAll: () => void;
  isTranslating: boolean;
  hasFiles: boolean;
  hasTranslatedFiles: boolean;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  onTranslate,
  onDownloadAll,
  isTranslating,
  hasFiles,
  hasTranslatedFiles
}) => {
  return (
    <div className="flex flex-wrap justify-center gap-4 p-6">
      <button
        onClick={onTranslate}
        disabled={isTranslating || !hasFiles}
        className={`px-6 py-3 rounded-lg text-white font-medium shadow-lg flex items-center space-x-2 transition-all ${
          isTranslating || !hasFiles
            ? 'bg-gray-700/50 cursor-not-allowed opacity-70'
            : 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/20'
        }`}
      >
        <FileText size={18} />
        <span>{isTranslating ? 'Translating...' : 'Translate Files'}</span>
      </button>
      
      <button
        onClick={onDownloadAll}
        disabled={!hasTranslatedFiles}
        className={`px-6 py-3 rounded-lg text-white font-medium shadow-lg flex items-center space-x-2 transition-all ${
          !hasTranslatedFiles
            ? 'bg-gray-700/50 cursor-not-allowed opacity-70'
            : 'bg-blue-600 hover:bg-blue-500 shadow-blue-500/20'
        }`}
      >
        <Download size={18} />
        <span>Download All</span>
      </button>
    </div>
  );
};

export default ActionButtons;