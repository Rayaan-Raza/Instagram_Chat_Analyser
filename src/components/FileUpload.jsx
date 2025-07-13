import React, { useCallback, useState } from 'react';
import JSZip from 'jszip';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, File, X, CheckCircle, Clock, BarChart3, Folder, FileText } from 'lucide-react';
import { useData } from '../contexts/DataContext';

const FileUpload = () => {
  const { uploadFile, uploadProcessedData, isLoading, setUserName } = useData();
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState('');
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [currentStep, setCurrentStep] = useState('');

  const processZipClientSide = async (file) => {
    setCurrentStep('Loading ZIP file...');
    setProgressPercentage(5);
    
    try {
      const zip = new JSZip();
      const zipContent = await zip.loadAsync(file);
      
      setCurrentStep('Scanning message folders...');
      setProgressPercentage(15);
      
      // Find all message files
      const messageFiles = [];
      const friendFolders = new Map();
      
      for (const [filePath, zipFile] of Object.entries(zipContent.files)) {
        if (filePath.includes('messages/inbox/') && filePath.endsWith('.json')) {
          messageFiles.push(filePath);
          
          // Extract friend folder name
          const parts = filePath.split('/');
          const inboxIndex = parts.indexOf('inbox');
          if (inboxIndex !== -1 && inboxIndex + 1 < parts.length) {
            const friendFolder = parts[inboxIndex + 1];
            if (!friendFolders.has(friendFolder)) {
              friendFolders.set(friendFolder, []);
            }
            friendFolders.get(friendFolder).push(filePath);
          }
        }
      }
      
      setCurrentStep(`Found ${friendFolders.size} friends, extracting data...`);
      setProgressPercentage(30);
      
      // Process each friend folder
      const friends = [];
      let friendId = 0;
      const totalFolders = friendFolders.size;
      let processedFolders = 0;
      
      for (const [folderName, files] of friendFolders) {
        // Update progress for each friend processed
        const folderProgress = 30 + (processedFolders / totalFolders) * 50; // 30% to 80%
        setProgressPercentage(Math.round(folderProgress));
        setCurrentStep(`Processing ${folderName}... (${processedFolders + 1}/${totalFolders})`);
        
        // Find the first message file to get participant info
        const firstMessageFile = files.find(f => f.endsWith('message_1.json'));
        
        if (firstMessageFile) {
          try {
            const content = await zipContent.file(firstMessageFile).async('string');
            const chatData = JSON.parse(content);
            
            if (chatData.participants && chatData.participants.length === 2) {
              // Get friend name (assume second participant is the friend)
              const friendName = chatData.participants[1]?.name || folderName.replace('_', ' ').title();
              
              // Extract messages for this friend
              const friendMessages = [];
              for (const filePath of files) {
                try {
                  const fileContent = await zipContent.file(filePath).async('string');
                  const fileData = JSON.parse(fileContent);
                  if (fileData.messages) {
                    friendMessages.push(...fileData.messages);
                  }
                } catch (e) {
                  console.log(`Error reading ${filePath}:`, e);
                }
              }
              
              friends.push({
                id: friendId++,
                name: friendName,
                chat_folder: folderName,
                message_files: files.length,
                total_messages: friendMessages.length,
                messages: friendMessages.slice(-1000), // Keep last 1000 messages
                analyzed: false
              });
            }
          } catch (e) {
            console.log(`Error processing ${folderName}:`, e);
          }
        }
        
        processedFolders++;
      }
      
      setCurrentStep(`Processed ${friends.length} friends, uploading data...`);
      setProgressPercentage(85);
      
      // Create a data object to send to backend
      const processedData = {
        friends: friends,
        user_name: 'User', // Will be updated by backend
        session_id: Date.now().toString()
      };
      
      setCurrentStep('Sending data to server...');
      setProgressPercentage(90);
      
      // Send processed data to backend
      const success = await sendProcessedData(processedData);
      if (success) {
        setProgressPercentage(100);
        setCurrentStep('Complete! Redirecting...');
        setTimeout(() => {
          setUploadedFiles([]);
          setUploadProgress('');
          setProgressPercentage(0);
          setCurrentStep('');
          navigate("/");
        }, 1000);
      }
      
    } catch (error) {
      console.error('Error processing ZIP:', error);
      setUploadProgress('Error processing ZIP file');
      setCurrentStep('Error occurred during processing');
      setProgressPercentage(0);
      setUploadedFiles([]);
    }
  };

  const sendProcessedData = async (data) => {
    return await uploadProcessedData(data);
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedFiles(acceptedFiles);
      
      if (file.name.endsWith('.zip')) {
        // Process ZIP client-side
        await processZipClientSide(file);
      } else if (file.name.endsWith('.json')) {
        // Handle single JSON file
        setCurrentStep('Processing JSON file...');
        setProgressPercentage(50);
        const success = await uploadFile(file);
        if (success) {
          setProgressPercentage(100);
          setCurrentStep('Complete! Redirecting...');
          setTimeout(() => {
            setUploadedFiles([]);
            setUploadProgress('');
            setProgressPercentage(0);
            setCurrentStep('');
            navigate("/");
          }, 1000);
        }
      }
    }
  }, [uploadFile, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
      'application/x-zip-compressed': ['.zip'],
      'application/json': ['.json']
    },
    multiple: false
  });

  const removeFile = () => {
    setUploadedFiles([]);
    setUploadProgress('');
    setProgressPercentage(0);
    setCurrentStep('');
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
            className="flex items-center justify-center space-x-3"
          >
            <File className="h-8 w-8 text-primary-600" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {uploadedFiles[0].name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(uploadedFiles[0].size / 1024 / 1024).toFixed(2)} MB
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
                {isDragActive ? 'Drop your messages here' : 'Upload Instagram Messages'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                Client-side processing - no large file uploads!
              </p>
              
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-left">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 font-medium">
                  How to get your Instagram messages:
                </p>
                <ol className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <li>1. Go to Instagram Settings → Privacy and Security → Data Download</li>
                  <li>2. Request your data and wait for the email</li>
                  <li>3. Download and extract the ZIP file</li>
                  <li>4. Navigate to <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">your_instagram_activity/messages/</code></li>
                  <li>5. Zip the entire <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">messages</code> folder</li>
                  <li>6. Upload the messages ZIP - processed in your browser!</li>
                </ol>
              </div>
              
              <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded p-3">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="text-left">
                    <p className="text-sm font-medium text-green-900 dark:text-green-100 mb-1">
                      Client-Side Processing
                    </p>
                    <ul className="text-xs text-green-700 dark:text-green-300 space-y-1">
                      <li>• ZIP processed in your browser</li>
                      <li>• Only extracted data sent to server</li>
                      <li>• No large file uploads</li>
                      <li>• Much faster processing</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State with Progress Bar */}
      {(isLoading || progressPercentage > 0) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 space-y-4"
        >
          {/* Progress Bar */}
          <div className="bg-gray-100 dark:bg-gray-800 rounded-full h-3 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>
          
          {/* Progress Text */}
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center space-x-2 text-primary-600">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <span className="font-medium">
                {progressPercentage === 100 ? 'Complete!' : 'Processing your messages...'}
              </span>
            </div>
            
            {currentStep && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {currentStep}
              </p>
            )}
            
            {progressPercentage > 0 && progressPercentage < 100 && (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {progressPercentage}% complete
              </p>
            )}
            
            <div className="flex items-center justify-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
              <Clock className="h-3 w-3" />
              <span>Processing in your browser - no server upload!</span>
            </div>
          </div>
          
          {/* Progress Details */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <BarChart3 className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-left">
                <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                  What's happening?
                </p>
                <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Reading ZIP file in your browser</li>
                  <li>• Extracting message data locally</li>
                  <li>• Sending only processed data to server</li>
                  <li>• Building your friend list instantly</li>
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