import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  Users, 
  MessageSquare, 
  Clock, 
  TrendingUp,
  User,
  Calendar,
  BarChart3,
  Search,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { useData } from '../contexts/DataContext';

const DashboardPage = () => {
  const { 
    friends, 
    networkAnalysis, 
    getNetworkAnalysis, 
    isLoading 
  } = useData();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredFriends, setFilteredFriends] = useState(friends);
  const [expandedCategory, setExpandedCategory] = useState(null);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredFriends(friends);
    } else {
      const filtered = friends.filter(friend =>
        friend.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredFriends(filtered);
    }
  }, [searchQuery, friends]);

  useEffect(() => {
    if (!networkAnalysis) {
      getNetworkAnalysis();
    }
  }, [networkAnalysis, getNetworkAnalysis]);

  const stats = [
    {
      icon: Users,
      label: 'Total Friends',
      value: friends.length,
      color: 'text-blue-600 dark:text-blue-400'
    },
    {
      icon: MessageSquare,
      label: 'Total Messages',
      value: networkAnalysis?.total_messages?.toLocaleString() || '0',
      color: 'text-green-600 dark:text-green-400'
    },
    {
      icon: TrendingUp,
      label: 'Most Active',
      value: networkAnalysis?.most_messages?.[0]?.friend?.name || 'N/A',
      color: 'text-purple-600 dark:text-purple-400'
    },
    {
      icon: Clock,
      label: 'Longest Friendship',
      value: networkAnalysis?.longest_friendships?.[0]?.friend?.name || 'N/A',
      color: 'text-orange-600 dark:text-orange-400'
    }
  ];

  const categories = [
    { name: 'Best Friends', count: networkAnalysis?.categories?.best_friends?.length || 0, color: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300' },
    { name: 'Close Friends', count: networkAnalysis?.categories?.close_friends?.length || 0, color: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' },
    { name: 'Regular Friends', count: networkAnalysis?.categories?.regular_friends?.length || 0, color: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' },
    { name: 'Occasional Friends', count: networkAnalysis?.categories?.occasional_friends?.length || 0, color: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300' },
    { name: 'Distant Friends', count: networkAnalysis?.categories?.distant_friends?.length || 0, color: 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Overview of your Instagram messaging patterns and social network
          </p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                className="stat-card"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      {stat.label}
                    </p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-3 rounded-full bg-gray-100 dark:bg-gray-800 ${stat.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Friends Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Friends List */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Your Friends
                </h2>
                <Link 
                  to="/network"
                  className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm font-medium"
                >
                  View Network Analysis →
                </Link>
              </div>

              {/* Search Bar */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search friends by name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>
              {searchQuery && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                  Found {filteredFriends.length} friend{filteredFriends.length !== 1 ? 's' : ''}
                </p>
              )}
              
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredFriends.slice(0, 10).map((friend, index) => (
                    <motion.div
                      key={friend.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4 + index * 0.05 }}
                    >
                      <Link
                        to={`/analysis/${friend.id}`}
                        className="flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                            <User className="h-5 w-5 text-primary-600" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {friend.name}
                            </p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Click to view analysis
                            </p>
                          </div>
                        </div>
                        <BarChart3 className="h-5 w-5 text-gray-400" />
                      </Link>
                    </motion.div>
                  ))}
                  
                  {filteredFriends.length > 10 && (
                    <div className="text-center pt-4">
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        And {filteredFriends.length - 10} more friends...
                      </p>
                    </div>
                  )}
                  {filteredFriends.length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-500 dark:text-gray-400">No friends found matching your search.</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Categories */}
          <div>
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Friendship Categories
              </h2>
              <div className="space-y-4">
                {categories.map((category, index) => {
                  // Get the friends for this category from networkAnalysis
                  const categoryKey = category.name.toLowerCase().replace(' ', '_');
                  const categoryFriends = networkAnalysis?.categories?.[categoryKey] || [];
                  return (
                    <motion.div
                      key={category.name}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      className="flex flex-col p-3 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <button
                        className="flex items-center w-full justify-between focus:outline-none"
                        onClick={() => setExpandedCategory(expandedCategory === category.name ? null : category.name)}
                      >
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${category.color.replace('bg-', 'bg-').replace('text-', '')}`}></div>
                          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                            {category.name}
                          </span>
                        </div>
                        <span className="text-sm font-semibold text-gray-600 dark:text-gray-300">
                          {category.count}
                        </span>
                        {expandedCategory === category.name ? (
                          <ChevronDown className="w-5 h-5 text-gray-500 ml-2" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-500 ml-2" />
                        )}
                      </button>
                      {expandedCategory === category.name && (
                        <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                          {categoryFriends.length === 0 && (
                            <div className="text-gray-500 text-sm">No friends in this category.</div>
                          )}
                          {categoryFriends.map((friend) => (
                            <Link
                              key={friend.friend.id}
                              to={`/analysis/${friend.friend.id}`}
                              className="block px-3 py-2 rounded hover:bg-blue-100 dark:hover:bg-gray-800 transition-colors"
                            >
                              <div className="flex justify-between items-center">
                                <span className="truncate text-gray-900 dark:text-gray-100">{friend.friend.name}</span>
                                <span className="text-xs text-gray-600 dark:text-gray-300">{friend.total_messages} msgs</span>
                              </div>
                            </Link>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card mt-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Quick Actions
              </h2>
              <div className="space-y-3">
                <Link
                  to="/network"
                  className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
                >
                  <Users className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    View Network Analysis
                  </span>
                </Link>
                <Link
                  to={`/analysis/${friends[0]?.id}`}
                  className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-200"
                >
                  <MessageSquare className="h-5 w-5 text-primary-600" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Analyze Top Friend
                  </span>
                </Link>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardPage; 