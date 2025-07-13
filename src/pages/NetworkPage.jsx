import React, { useState, useEffect } from 'react';
import { useData } from '../contexts/DataContext';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Info } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const NetworkPage = () => {
  const { getNetworkAnalysis, isLoading } = useData();
  const [networkData, setNetworkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    fetchNetworkData();
  }, []);

  const fetchNetworkData = async () => {
    try {
      setLoading(true);
      const networkAnalysis = await getNetworkAnalysis();
      
      if (networkAnalysis) {
        setNetworkData(networkAnalysis);
      } else {
        setError('Failed to fetch network data');
      }
    } catch (err) {
      setError('Failed to fetch network data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!networkData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-gray-600 mb-4">No Data</h2>
          <p className="text-gray-600">No network data available.</p>
        </div>
      </div>
    );
  }

  const categoryData = [
    { name: 'Best Friends', value: networkData.categories.best_friends.length, fill: '#FF6B6B' },
    { name: 'Close Friends', value: networkData.categories.close_friends.length, fill: '#4ECDC4' },
    { name: 'Regular Friends', value: networkData.categories.regular_friends.length, fill: '#45B7D1' },
    { name: 'Occasional Friends', value: networkData.categories.occasional_friends.length, fill: '#96CEB4' },
    { name: 'Distant Friends', value: networkData.categories.distant_friends.length, fill: '#FFEAA7' }
  ];

  const CustomTooltip = ({ text }) => (
    <span className="relative group cursor-pointer">
      <Info className="inline w-4 h-4 ml-1 text-gray-400 group-hover:text-blue-500" />
      <span className="absolute left-1/2 z-10 hidden group-hover:block bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-pre w-64 -translate-x-1/2 mt-2 shadow-lg">
        {text}
      </span>
    </span>
  );

  // Custom tick for dark mode support with angle
  const { isDark } = useTheme();
  const AngleTick = (props) => {
    const { x, y, payload } = props;
    return (
      <text
        x={x}
        y={y + 15}
        textAnchor="end"
        fill={isDark ? '#fff' : '#1f2937'}
        style={{ fontSize: 12 }}
        transform={`rotate(-45, ${x}, ${y + 15})`}
      >
        {payload.value}
      </text>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6"
        >
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-2">Social Network Analysis</h1>
          <p className="text-gray-600 dark:text-gray-300">
            {networkData.total_friends} friends • {networkData.total_messages.toLocaleString()} total messages
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Friendship Categories */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Friendship Categories</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Most Active Friends */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Most Active Friends</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={networkData.most_messages.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="friend.name"
                  height={80}
                  tickLine={false}
                  interval={0}
                  tick={<AngleTick />}
                />
                <YAxis tick={{ fill: '#6b7280' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', color: '#fff', borderRadius: 8 }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="total_messages" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Top Lists */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
          {/* Most Messages */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4">Most Messages</h3>
            <div className="space-y-3">
              {networkData.most_messages.slice(0, 5).map((friend, index) => (
                <Link
                  key={friend.friend.id}
                  to={`/analysis/${friend.friend.id}`}
                  className="block p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-blue-800">{friend.friend.name}</span>
                    <span className="text-blue-600 font-bold">{friend.total_messages}</span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>

          {/* Most Balanced */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4">Most Balanced</h3>
            <div className="space-y-3">
              {networkData.most_balanced.slice(0, 5).map((friend, index) => (
                <Link
                  key={friend.friend.id}
                  to={`/analysis/${friend.friend.id}`}
                  className="block p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-green-800">{friend.friend.name}</span>
                    <span className="text-green-600 font-bold">{friend.your_percentage.toFixed(0)}%</span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>

          {/* Longest Friendships */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4">Longest Friendships</h3>
            <div className="space-y-3">
              {networkData.longest_friendships.slice(0, 5).map((friend, index) => (
                <Link
                  key={friend.friend.id}
                  to={`/analysis/${friend.friend.id}`}
                  className="block p-3 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-purple-800">{friend.friend.name}</span>
                    <span className="text-purple-600 font-bold">{friend.friendship_duration_days.toFixed(0)}d</span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>

          {/* Fastest Responses */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-100 mb-4">Fastest Responses</h3>
            <div className="space-y-3">
              {networkData.fastest_responses.slice(0, 5).map((friend, index) => (
                <Link
                  key={friend.friend.id}
                  to={`/analysis/${friend.friend.id}`}
                  className="block p-3 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-orange-800">{friend.friend.name}</span>
                    <span className="text-orange-600 font-bold">
                      {friend.their_avg_response < 60 
                        ? `${friend.their_avg_response.toFixed(0)}s`
                        : `${(friend.their_avg_response / 60).toFixed(0)}m`
                      }
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Category Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6"
        >
          <div className="flex items-center mb-4">
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mr-2">Friendship Categories Breakdown</h2>
            <CustomTooltip text={
              `Friendship categories are based on message volume and frequency:
- Best Friends: 1000+ messages, 2+/day
- Close Friends: 500+ messages, 1+/day
- Regular Friends: 200+ messages, 0.5+/day
- Occasional Friends: 50+ messages
- Distant Friends: Fewer than 50 messages`
            } />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(networkData.categories).map(([category, friends]) => (
              <div key={category} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3 capitalize">
                  {category.replace('_', ' ')} ({friends.length})
                </h3>
                <div className="space-y-2">
                  {friends.slice(0, 3).map((friend) => (
                    <Link
                      key={friend.friend.id}
                      to={`/analysis/${friend.friend.id}`}
                      className="block p-2 bg-white dark:bg-gray-800 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-900 dark:text-gray-100 truncate">{friend.friend.name}</span>
                        <span className="text-sm text-gray-700 dark:text-gray-300">{friend.total_messages} msgs</span>
                      </div>
                    </Link>
                  ))}
                  {friends.length > 3 && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                      +{friends.length - 3} more friends
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default NetworkPage; 