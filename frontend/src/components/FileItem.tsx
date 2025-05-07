import React from 'react';
import { FileItem as FileItemType } from '../types';
import { formatFileSize, getFileTypeIcon } from '../utils/fileUtils';
import { Download, Trash2, FileIcon } from 'lucide-react';
import * as Icons from 'lucide-react';

interface FileItemProps {
  file: FileItemType;
  onDownload: (file: FileItemType) => void;
  onRemove?: (id: string) => void;
}

const FileItem: React.FC<FileItemProps> = ({ file, onDownload, onRemove }) => {
  const StatusBadge = () => {
    let bgColor = '';
    let textColor = '';
    
    switch(file.status) {
      case 'pending':
        bgColor = 'bg-yellow-500/20';
        textColor = 'text-yellow-300';
        break;
      case 'translating':
        bgColor = 'bg-blue-500/20';
        textColor = 'text-blue-300';
        break;
      case 'translated':
        bgColor = 'bg-green-500/20';
        textColor = 'text-green-300';
        break;
      case 'error':
        bgColor = 'bg-red-500/20';
        textColor = 'text-red-300';
        break;
    }
    
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${bgColor} ${textColor}`}>
        {file.status}
      </span>
    );
  };

  // Get the appropriate icon component
  const iconName = getFileTypeIcon(file.type) as keyof typeof Icons;
  const IconComponent = (Icons[iconName] || FileIcon) as React.ElementType;
  
  return (
    <div className="group flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-all">
      <div className="flex items-center space-x-4">
        <div className="text-blue-400 bg-blue-400/10 p-2 rounded-lg">
          <IconComponent size={24} />
        </div>
        <div>
          <p className="text-white font-medium text-sm">{file.name}</p>
          <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
        </div>
      </div>
      <div className="flex items-center space-x-3">
        {file.status === 'translating' && (
          <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${file.progress}%` }}
            />
          </div>
        )}
        <StatusBadge />
        {file.status === 'translated' && (
          <button
            onClick={() => onDownload(file)}
            className="p-2 rounded-lg text-blue-400 hover:bg-blue-500/10 transition-colors"
            title="Download"
          >
            <Download size={18} />
          </button>
        )}
        {onRemove && (
          <button
            onClick={() => onRemove(file.id)}
            className="opacity-0 group-hover:opacity-100 p-2 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all"
            title="Remove"
          >
            <Trash2 size={18} />
          </button>
        )}
      </div>
    </div>
  );
};

export default FileItem;