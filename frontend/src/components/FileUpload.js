import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const UploadSection = styled.div`
  background-color: #1e1e1e;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  margin-bottom: 2rem;
`;

const UploadTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 1rem;
  color: #e0e0e0;
`;

const FileInputContainer = styled.div`
  position: relative;
  margin-bottom: 1rem;
`;

const FileInput = styled.input`
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
`;

const FileInputLabel = styled.label`
  display: block;
  padding: 1rem;
  border: 2px dashed #5e60ce;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #b0b0b0;

  &:hover {
    border-color: #7c3aed;
    background-color: rgba(94, 96, 206, 0.1);
  }
`;

const UploadButton = styled.button`
  background-color: #5e60ce;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  margin-right: 1rem;

  &:hover {
    background-color: #4c4fb8;
  }

  &:disabled {
    background-color: #333;
    cursor: not-allowed;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: #333;
  border-radius: 4px;
  margin: 1rem 0;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  height: 100%;
  background-color: #5e60ce;
  transition: width 0.3s ease;
  width: ${props => props.progress}%;
`;

const FileList = styled.div`
  margin-top: 1rem;
`;

const FileItem = styled.div`
  padding: 0.5rem;
  background-color: #2a2a2a;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const FileName = styled.span`
  color: #e0e0e0;
`;

const FileSize = styled.span`
  color: #b0b0b0;
  font-size: 0.9rem;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(255, 107, 107, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 107, 107, 0.3);
`;

const SuccessMessage = styled.div`
  color: #51cf66;
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(81, 207, 102, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(81, 207, 102, 0.3);
`;

const FileUpload = ({ onUploadComplete, isAdmin = false }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef();

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    setError('');
    setSuccess('');
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select files to upload');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError('');
    setSuccess('');

    try {
      const uploadPromises = selectedFiles.map(async (file, index) => {
        const formData = new FormData();
        formData.append('file', file);

        const endpoint = isAdmin ? '/upload/global' : '/upload';
        
        const response = await axios.post(endpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const fileProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            const totalProgress = Math.round(
              ((index + fileProgress / 100) / selectedFiles.length) * 100
            );
            setProgress(totalProgress);
          },
        });

        return response.data;
      });

      await Promise.all(uploadPromises);
      
      setSuccess(`Successfully uploaded ${selectedFiles.length} file(s)`);
      setSelectedFiles([]);
      setProgress(100);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      if (onUploadComplete) {
        onUploadComplete();
      }

    } catch (error) {
      console.error('Upload failed:', error);
      setError(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 2000);
    }
  };

  return (
    <UploadSection>
      <UploadTitle>
        Upload Photos {isAdmin && '(Global)'}
      </UploadTitle>
      
      <FileInputContainer>
        <FileInput
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={handleFileSelect}
          id="file-upload"
        />
        <FileInputLabel htmlFor="file-upload">
          Click here or drag and drop files to upload
        </FileInputLabel>
      </FileInputContainer>

      {selectedFiles.length > 0 && (
        <FileList>
          {selectedFiles.map((file, index) => (
            <FileItem key={index}>
              <FileName>{file.name}</FileName>
              <FileSize>{formatFileSize(file.size)}</FileSize>
            </FileItem>
          ))}
        </FileList>
      )}

      {uploading && (
        <ProgressBar>
          <ProgressFill progress={progress} />
        </ProgressBar>
      )}

      <UploadButton 
        onClick={handleUpload} 
        disabled={uploading || selectedFiles.length === 0}
      >
        {uploading ? `Uploading... ${progress}%` : 'Upload Files'}
      </UploadButton>

      {error && <ErrorMessage>{error}</ErrorMessage>}
      {success && <SuccessMessage>{success}</SuccessMessage>}
    </UploadSection>
  );
};

export default FileUpload;
