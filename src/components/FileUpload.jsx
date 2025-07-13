import React, { useCallback, useState } from 'react';
import JSZip from 'jszip';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import { useData } from '../contexts/DataContext';

const FileUpload = () => {
  const { uploadFile, isLoading, setUserName } = useData();
  const navigate = useNavigate();
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFile(file);
      // Read ZIP and extract user name from second participant in first message_1.json
      try {
        const zip = await JSZip.loadAsync(file);
        // Find the first message_1.json file in the inbox
        const inboxFolder = Object.keys(zip.files).find(f => f.includes('messages/inbox/'));
        let messageFile = null;
        for (const path in zip.files) {
          if (path.includes('messages/inbox/') && path.endsWith('message_1.json')) {
            messageFile = path;
            break;
          }
        }
        if (messageFile) {
          const content = await zip.file(messageFile).async('string');
          const json = JSON.parse(content);
          if (json.participants && json.participants.length >= 2) {
            const userName = json.participants[1].name;
            setUserName(userName);
            const success = await uploadFile(file);
            if (success) {
              setUploadedFile(null);
              navigate("/");
            }
            return;
          }
        }
        // fallback: upload with no userName
        const success = await uploadFile(file);
        if (success) {
          setUploadedFile(null);
          navigate("/");
        }
      } catch (e) {
        // fallback: upload with no userName
        const success = await uploadFile(file);
        if (success) {
          setUploadedFile(null);
          navigate("/");
        }
      }
    }
  }, [uploadFile, setUserName, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip']
    },
    multiple: false,
    maxFiles: 1
  });

  const removeFile = () => {
    setUploadedFile(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* User Name Input */}
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
        }`}
      >
        <input {...getInputProps()} />
        
        {uploadedFile ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center space-x-3"
          >
            <File className="h-8 w-8 text-primary-600" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {uploadedFile.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                removeFile();
              }}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </motion.div>
        ) : (
          <div className="space-y-4">
            <motion.div
              animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
              transition={{ duration: 0.2 }}
            >
              <Upload className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            </motion.div>
            
            <div>
              <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {isDragActive ? 'Drop your Instagram data here' : 'Upload Instagram Data'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Drag and drop your Instagram data ZIP file, or click to browse
              </p>
              
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-left">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 font-medium">
                  How to get your Instagram data:
                </p>
                <ol className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <li>1. Go to Instagram Settings → Privacy and Security → Data Download</li>
                  <li>2. Request your data and wait for the email</li>
                  <li>3. Download the ZIP file to your computer</li>
                  <li>4. Upload the ZIP file here</li>
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 flex items-center justify-center space-x-2 text-primary-600"
        >
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
          <span>Analyzing your Instagram data...</span>
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload; 