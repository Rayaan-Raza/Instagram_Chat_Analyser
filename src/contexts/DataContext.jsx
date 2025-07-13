import React, { createContext, useContext, useState } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';

const DataContext = createContext();

// Get API base URL from environment variable or use relative URL for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Debug logging
console.log('Environment check:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  API_BASE_URL: API_BASE_URL,
  NODE_ENV: import.meta.env.NODE_ENV
});

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [friends, setFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null);
  const [friendAnalysis, setFriendAnalysis] = useState({});
  const [networkAnalysis, setNetworkAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userName, setUserName] = useState('Rayaan Raza');
  const [sessionId, setSessionId] = useState(null);

  const uploadFile = async (file) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_name', userName);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setSessionId(response.data.session_id);
        setFriends(response.data.friends);
        toast.success('File uploaded successfully!');
        return true;
      } else {
        toast.error(response.data.error || 'Upload failed');
        return false;
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.error || 'Upload failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const getFriendAnalysis = async (friendId) => {
    if (!sessionId) return;

    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analysis/${friendId}?session_id=${sessionId}`);
      
      if (response.data.success) {
        setFriendAnalysis(prev => ({
          ...prev,
          [friendId]: response.data.analysis
        }));
        return response.data.analysis;
      } else {
        toast.error(response.data.error || 'Failed to get analysis');
        return null;
      }
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.response?.data?.error || 'Failed to get analysis');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const getNetworkAnalysis = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/network?session_id=${sessionId}`);
      
      if (response.data.success) {
        setNetworkAnalysis(response.data.network);
        return response.data.network;
      } else {
        toast.error(response.data.error || 'Failed to get network analysis');
        return null;
      }
    } catch (error) {
      console.error('Network analysis error:', error);
      toast.error(error.response?.data?.error || 'Failed to get network analysis');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const getFriendDetails = async (friendId) => {
    if (!sessionId) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/api/friend-details/${friendId}?session_id=${sessionId}`);
      
      if (response.data.success) {
        return response.data.details;
      } else {
        toast.error(response.data.error || 'Failed to get friend details');
        return null;
      }
    } catch (error) {
      console.error('Friend details error:', error);
      toast.error(error.response?.data?.error || 'Failed to get friend details');
      return null;
    }
  };

  const getQuickStats = async (friendId) => {
    if (!sessionId) return;

    try {
      const response = await axios.get(`${API_BASE_URL}/api/quick-stats/${friendId}?session_id=${sessionId}`);
      
      if (response.data.success) {
        return response.data.quick_stats;
      } else {
        toast.error(response.data.error || 'Failed to get quick stats');
        return null;
      }
    } catch (error) {
      console.error('Quick stats error:', error);
      toast.error(error.response?.data?.error || 'Failed to get quick stats');
      return null;
    }
  };

  const clearData = () => {
    setFriends([]);
    setSelectedFriend(null);
    setFriendAnalysis({});
    setNetworkAnalysis(null);
    setSessionId(null);
  };

  const value = {
    friends,
    selectedFriend,
    setSelectedFriend,
    friendAnalysis,
    networkAnalysis,
    isLoading,
    userName,
    setUserName,
    sessionId,
    uploadFile,
    getFriendAnalysis,
    getFriendDetails,
    getQuickStats,
    getNetworkAnalysis,
    clearData,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
}; 