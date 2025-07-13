import React, { useCallback, useState } from 'react';
import JSZip from 'jszip';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, File, X, CheckCircle, Clock, BarChart3, Folder, FileText } from 'lucide-react';
import { useData } from '../contexts/DataContext';

const FileUpload = () => {
  const { uploadFile, isLoading, setUserName } = useData();
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState('');

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploadedFiles(acceptedFiles);
    setUploadProgress('Processing files...');
    
    try {
      // Handle multiple files
      if (acceptedFiles.length > 1) {
        // Multiple JSON files - create a ZIP
        setUploadProgress('Creating ZIP from multiple files...');
        const zip = new JSZip();
        
        for (const file of acceptedFiles) {
          const content = await file.text();
          zip.file(file.name, content);
        }
        
        const zipBlob = await zip.generateAsync({ type: 'blob' });
        const zipFile = new File([zipBlob], 'messages.zip', { type: 'application/zip' });
        
        setUploadProgress('Uploading and analyzing data...');
        const success = await uploadFile(zipFile);
        if (success) {
          setUploadedFiles([]);
          setUploadProgress('');
          navigate("/");
        }
        return;
      }
      
      // Single file
      const file = acceptedFiles[0];
      
      if (file.name.endsWith('.json')) {
        // Single JSON file
        setUploadProgress('Processing JSON file...');
        
        // Try to extract user name from the JSON
        try {
          const content = await file.text();
          const json = JSON.parse(content);
          if (json.participants && json.participants.length >= 2) {
            const userName = json.participants[1].name;
            setUserName(userName);
          }
        } catch (e) {
          console.log('Could not extract user name from JSON');
        }
        
        setUploadProgress('Uploading and analyzing data...');
        const success = await uploadFile(file);
        if (success) {
          setUploadedFiles([]);
          setUploadProgress('');
          navigate("/");
        }
        return;
      }
      
      // ZIP file - extract user name
      setUploadProgress('Reading ZIP file...');
      try {
        const zip = await JSZip.loadAsync(file);
        // Find the first message_1.json file in the inbox
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
          }
        }
      } catch (e) {
        console.log('Could not extract user name from ZIP');
      }
      
      setUploadProgress('Uploading and analyzing data...');
      const success = await uploadFile(file);
      if (success) {
        setUploadedFiles([]);
        setUploadProgress('');
        navigate("/");
      }
      
    } catch (e) {
      console.error('Upload error:', e);
      setUploadProgress('');
      setUploadedFiles([]);
    }
  }, [uploadFile, setUserName, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip'],
      'application/json': ['.json']
    },
    multiple: true
  });

  const removeFile = (index) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
    setUploadProgress('');
  };

  const removeAllFiles = () => {
    setUploadedFiles([]);
    setUploadProgress('');
  };

  return (
    <div className="max-w-2xl mx-auto">
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
        
        {uploadedFiles.length > 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {uploadedFiles.length} file(s) selected
              </h3>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeAllFiles();
                }}
                className="text-sm text-red-500 hover:text-red-700"
              >
                Remove all
              </button>
            </div>
            
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded p-2">
                  <div className="flex items-center space-x-2">
                    {file.name.endsWith('.json') ? (
                      <FileText className="h-4 w-4 text-blue-600" />
                    ) : (
                      <File className="h-4 w-4 text-green-600" />
                    )}
                    <div className="text-left">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {file.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(index);
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
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
                {isDragActive ? 'Drop your messages here' : 'Upload Instagram Messages'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Upload the messages folder or individual message files for faster processing
              </p>
              
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-left">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 font-medium">
                  How to get your Instagram messages:
                </p>
                <ol className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <li>1. Go to Instagram Settings → Privacy and Security → Data Download</li>
                  <li>2. Request your data and wait for the email</li>
                  <li>3. Download and extract the ZIP file</li>
                  <li>4. Navigate to: <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">your_instagram_activity/messages/</code></li>
                  <li>5. Upload the entire <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">messages</code> folder or individual JSON files</li>
                </ol>
              </div>
              
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded p-3">
                  <div className="flex items-center space-x-2 mb-1">
                    <Folder className="h-4 w-4 text-blue-600" />
                    <span className="text-xs font-medium text-blue-900 dark:text-blue-100">Option 1: Messages Folder</span>
                  </div>
                  <p className="text-xs text-blue-700 dark:text-blue-300">
                    Zip the entire <code>messages</code> folder and upload
                  </p>
                </div>
                
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded p-3">
                  <div className="flex items-center space-x-2 mb-1">
                    <FileText className="h-4 w-4 text-green-600" />
                    <span className="text-xs font-medium text-green-900 dark:text-green-100">Option 2: Individual Files</span>
                  </div>
                  <p className="text-xs text-green-700 dark:text-green-300">
                    Upload multiple <code>message_*.json</code> files directly
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State with Progress */}
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 space-y-4"
        >
          <div className="flex items-center justify-center space-x-2 text-primary-600">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
            <span className="font-medium">Processing your messages...</span>
          </div>
          
          {uploadProgress && (
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {uploadProgress}
              </p>
              <div className="flex items-center justify-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                <Clock className="h-3 w-3" />
                <span>Lightning fast - no file extraction needed!</span>
              </div>
            </div>
          )}
          
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <BarChart3 className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-left">
                <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                  What's happening?
                </p>
                <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Reading ZIP directly (no extraction)</li>
                  <li>• Scanning message folders</li>
                  <li>• Building friend list instantly</li>
                  <li>• Ready to browse immediately</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default FileUpload; 