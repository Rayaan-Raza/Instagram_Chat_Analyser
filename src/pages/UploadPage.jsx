import React from 'react';
import { motion } from 'framer-motion';
import { Instagram, BarChart3, Users, Clock, MessageSquare } from 'lucide-react';
import FileUpload from '../components/FileUpload';

const UploadPage = () => {
  const features = [
    {
      icon: MessageSquare,
      title: 'Message Analysis',
      description: 'Analyze your conversation patterns, word usage, and message lengths'
    },
    {
      icon: Clock,
      title: 'Timing Insights',
      description: 'Discover when you\'re most active and your messaging habits'
    },
    {
      icon: Users,
      title: 'Social Network',
      description: 'See your friendship rankings and social network overview'
    },
    {
      icon: BarChart3,
      title: 'Response Times',
      description: 'Track response patterns and conversation gaps'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-primary-100 dark:bg-primary-900/30 rounded-full">
            <Instagram className="h-12 w-12 text-primary-600" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          Instagram Message Analyzer
        </h1>
        
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          Discover insights about your Instagram messaging patterns, social network, and communication habits
        </p>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
      >
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="card text-center"
            >
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-full">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="card max-w-4xl mx-auto"
      >
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Get Started
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Upload your Instagram data to begin analyzing your messaging patterns
          </p>
        </div>
        
        <FileUpload />
      </motion.div>

      {/* Privacy Note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="mt-8 text-center"
      >
        <p className="text-sm text-gray-500 dark:text-gray-400">
          🔒 Your data is processed locally and never stored permanently. 
          All analysis is done on your device for maximum privacy.
        </p>
      </motion.div>
    </div>
  );
};

export default UploadPage; 