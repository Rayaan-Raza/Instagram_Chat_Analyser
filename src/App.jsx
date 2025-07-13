import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { motion } from 'framer-motion';
import Header from './components/Header';
import UploadPage from './pages/UploadPage';
import DashboardPage from './pages/DashboardPage';
import FriendAnalysisPage from './pages/FriendAnalysisPage';
import NetworkPage from './pages/NetworkPage';
import { useData } from './contexts/DataContext';

function App() {
  const { sessionId } = useData();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <motion.main
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="container mx-auto px-4 py-8"
      >
        <Routes>
          <Route 
            path="/" 
            element={sessionId ? <DashboardPage /> : <UploadPage />} 
          />
          <Route 
            path="/analysis/:friendId" 
            element={sessionId ? <FriendAnalysisPage /> : <UploadPage />} 
          />
          <Route 
            path="/network" 
            element={sessionId ? <NetworkPage /> : <UploadPage />} 
          />
        </Routes>
      </motion.main>
    </div>
  );
}

export default App; 