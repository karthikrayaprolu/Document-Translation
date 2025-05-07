import { useState } from 'react';
import { FileItem } from '../types';

const API_URL = 'http://localhost:5000';

export const useTranslation = (files: FileItem[], setFiles: React.Dispatch<React.SetStateAction<FileItem[]>>) => {
  const [isTranslating, setIsTranslating] = useState(false);

  const handleSubmitForTranslation = async () => {
    if (files.length === 0) return;

    setIsTranslating(true);
    const formData = new FormData();
    
    files.forEach(file => {
      if (file.status === 'pending') {
        formData.append('files[]', file.file);
        // Update file status to translating
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'translating' } : f
        ));
      }
    });

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(prev => prev.map(f => {
          const fileStatus = data.find((status: any) => status.fileName === f.name);
          if (fileStatus) {
            return {
              ...f,
              status: fileStatus.status,
              error: fileStatus.error
            };
          }
          return f;
        }));
      } else {
        throw new Error('Translation failed');
      }
    } catch (error) {
      console.error('Translation error:', error);
      // Update failed files to error status
      setFiles(prev => prev.map(f => 
        f.status === 'translating' ? { ...f, status: 'error' } : f
      ));
    } finally {
      setIsTranslating(false);
    }
  };

  return {
    isTranslating,
    handleSubmitForTranslation
  };
};