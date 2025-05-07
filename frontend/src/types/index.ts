export interface FileItem {
  id: string;
  name: string;
  type: string;
  size: number;
  file: File;
  path: string;
  status: 'pending' | 'translating' | 'translated' | 'error';
  progress: number;
  error?: string;
}