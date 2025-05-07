import { useState, useCallback } from 'react';
import { FileItem } from '../types';

export const useFileUpload = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const items = e.dataTransfer.items;
    const newFiles: FileItem[] = [];

    const processFile = (file: File, path: string = '') => {
      newFiles.push(createFileItem(file, path));
    };

    const processDirectory = async (entry: any, path: string = '') => {
      const reader = entry.createReader();
      const entries = await new Promise<any[]>((resolve) => {
        reader.readEntries(resolve);
      });

      for (const entry of entries) {
        if (entry.isFile) {
          const file = await new Promise<File>((resolve) => {
            entry.file(resolve);
          });
          processFile(file, path);
        } else if (entry.isDirectory) {
          const newPath = path ? `${path}/${entry.name}` : entry.name;
          await processDirectory(entry, newPath);
        }
      }
    };

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.kind === 'file') {
        const entry = item.webkitGetAsEntry();
        if (entry) {
          if (entry.isFile) {
            const file = item.getAsFile();
            if (file) processFile(file);
          } else if (entry.isDirectory) {
            processDirectory(entry);
          }
        }
      }
    }

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    const newFiles = Array.from(e.target.files).map(file => {
      const path = file.webkitRelativePath || '';
      return createFileItem(file, path);
    });
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const createFileItem = (file: File, path: string = ''): FileItem => ({
    id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    name: file.name,
    type: file.type,
    size: file.size,
    file: file,
    path: path,
    status: 'pending',
    progress: 0
  });

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(file => file.id !== id));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  return {
    files,
    setFiles,
    isDragging,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    removeFile,
    clearFiles
  };
};