import React from 'react';
import { FileItem as FileItemType } from '../types';
import FileItem from './FileItem';
import { Files, Folder } from 'lucide-react';

interface FileListProps {
  files: FileItemType[];
  onDownload: (file: FileItemType) => void;
  onRemove?: (id: string) => void;
}

const FileList: React.FC<FileListProps> = ({ files, onDownload, onRemove }) => {
  if (files.length === 0) return null;

  // Group files by their folder path
  const groupedFiles = files.reduce((acc, file) => {
    const folderPath = file.path ? file.path.split('/').slice(0, -1).join('/') : '';
    if (!acc[folderPath]) {
      acc[folderPath] = [];
    }
    acc[folderPath].push(file);
    return acc;
  }, {} as Record<string, FileItemType[]>);

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm shadow-lg p-6 rounded-xl border border-white/5">
      <div className="flex items-center space-x-3 mb-6">
        <Files size={20} className="text-blue-400" />
        <h2 className="text-lg font-semibold text-white">Uploaded Files</h2>
        <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded-full">
          {files.length} file{files.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      <div className="space-y-4 max-h-[40vh] overflow-y-auto pr-2 custom-scrollbar">
        {Object.entries(groupedFiles).map(([folderPath, folderFiles]) => (
          <div key={folderPath} className="space-y-2">
            {folderPath && (
              <div className="flex items-center space-x-2 text-gray-400">
                <Folder size={16} />
                <span className="text-sm">{folderPath}</span>
              </div>
            )}
            <div className="space-y-2 pl-4">
              {folderFiles.map((file) => (
                <FileItem 
                  key={file.id} 
                  file={file} 
                  onDownload={onDownload}
                  onRemove={onRemove}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileList;