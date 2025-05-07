import { FileItem } from '../types';

const API_URL = 'http://localhost:5000';

// Utility functions for file handling
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

export const getFileTypeIcon = (mimeType: string): string => {
  if (mimeType.includes('pdf')) return 'FileText';
  if (mimeType.includes('image')) return 'Image';
  if (mimeType.includes('text')) return 'File';
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'Table';
  return 'File';
};

// Download helpers
const createDownloadLink = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

const handleDownloadError = async (response: Response): Promise<string> => {
  try {
    const errorData = await response.json();
    return errorData.error || `Download failed: ${response.statusText}`;
  } catch {
    return `Download failed: ${response.statusText}`;
  }
};

// Main download functions
export const downloadFile = async (file: FileItem): Promise<void> => {
  if (!file || !file.name) {
    throw new Error('Invalid file data');
  }

  try {
    const translatedFileName = `${file.name.replace('.pdf', '')}_translated.xlsx`;
    const response = await fetch(`${API_URL}/download/${encodeURIComponent(translatedFileName)}`);
    
    if (!response.ok) {
      const errorMessage = await handleDownloadError(response);
      throw new Error(errorMessage);
    }

    const blob = await response.blob();
    createDownloadLink(blob, translatedFileName);
  } catch (error) {
    console.error('Download error:', error);
    throw error instanceof Error ? error : new Error('Unknown download error');
  }
};

export const downloadAllFiles = async (files: FileItem[]): Promise<void> => {
  const translatedFiles = files.filter(f => f.status === 'translated');
  
  if (translatedFiles.length === 0) {
    throw new Error('No translated files available for download');
  }

  try {
    const response = await fetch(`${API_URL}/download-all`);
    
    if (!response.ok) {
      const errorMessage = await handleDownloadError(response);
      throw new Error(errorMessage);
    }

    const blob = await response.blob();
    createDownloadLink(blob, 'translated_documents.zip');
  } catch (error) {
    console.error('Download error:', error);
    throw error instanceof Error ? error : new Error('Unknown download error');
  }
};