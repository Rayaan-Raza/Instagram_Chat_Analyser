import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useData } from '../contexts/DataContext';
import { motion } from 'framer-motion';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { Info } from 'lucide-react';

// Add a simple Tooltip component
const CustomTooltip = ({ text }) => (
  <span className="relative group cursor-pointer">
    <Info className="inline w-4 h-4 ml-1 text-gray-400 group-hover:text-blue-500" />
    <span className="absolute left-1/2 z-10 hidden group-hover:block bg-gray-900 text-white text-xs rounded px-2 py-1 whitespace-pre w-64 -translate-x-1/2 mt-2 shadow-lg">
      {text}
    </span>
  </span>
);

const FriendAnalysisPage = () => {
  const { friendId } = useParams();
  const { sessionId } = useData();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    if (sessionId && friendId) {
      fetchAnalysis();
    }
  }, [sessionId, friendId]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/analysis/${friendId}?session_id=${sessionId}`);
      const data = await response.json();
      
      if (data.success) {
        setAnalysis(data.analysis);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Failed to fetch analysis data');
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

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold text-gray-600 mb-4">No Data</h2>
          <p className="text-gray-600">No analysis data available for this friend.</p>
        </div>
      </div>
    );
  }

  // Log the analysis object for debugging
  console.log('Friend analysis:', analysis);

  const friendName = analysis.friend?.name || 'Unknown';
  const yourWords = Array.isArray(analysis.your_words) ? analysis.your_words : [];
  const theirWords = Array.isArray(analysis.their_words) ? analysis.their_words : [];
  const yourTiming = analysis.your_timing || {};
  // Debug: log daily timing data
  console.log('yourTiming.daily', yourTiming.daily);
  const timingData = Array.isArray(yourTiming.hourly) ? yourTiming.hourly : [];
  // Ensure all 24 hours are present for the chart
  const fullTimingData = Array.from({ length: 24 }, (_, hour) => {
    const found = timingData.find((d) => d.hour === hour);
    return { hour, count: found ? found.count : 0 };
  });
  // Prepare data for day of week bar chart
  const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const dailyData = dayOrder.map(day => {
    const found = (yourTiming.daily || []).find(d => d.day === day);
    return { day, count: found ? found.count : 0 };
  });

  const messageDistributionData = [
    { name: 'You', value: analysis.your_messages || 0, fill: '#0088FE' },
    { name: friendName, value: analysis.their_messages || 0, fill: '#00C49F' }
  ];

  // Custom tick for axis labels (white in Tailwind dark mode, gray-900 in light)
  const AxisTick = (props) => {
    const { x, y, payload } = props;
    // Check Tailwind's dark mode class
    const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark');
    return (
      <text
        x={x}
        y={y + 16}
        textAnchor="middle"
        fill={isDark ? '#fff' : '#1f2937'}
        fontSize={14}
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
          <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-2">
            Analysis with {friendName}
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            {analysis.total_messages?.toLocaleString() || '0'} total messages • 
            {analysis.friendship_duration_days?.toFixed(0) || '0'} days of friendship
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Message Distribution */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Message Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={messageDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {messageDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Messages by Day of Week Bar Chart */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Messages by Day of Week</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="day"
                  ticks={['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
                  interval={0}
                  tick={<AxisTick />}
                />
                <YAxis allowDecimals={false} tick={<AxisTick />} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366F1" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Average Messages by Hour Line Chart */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Average Messages by Hour</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={fullTimingData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" type="number" domain={[0, 23]} ticks={Array.from({length: 24}, (_, i) => i)} label={{ value: 'Hour of Day', position: 'insideBottomRight', offset: -5 }} />
                <YAxis label={{ value: 'Messages', angle: -90, position: 'insideLeft' }} allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#4F46E5" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Messages" />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Response Times */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center mb-4">
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mr-2">Response Times</h2>
              <CustomTooltip text={
                `Response time is the average time it takes for you or your friend to reply to a message.

- Instant: < 1 min
- Quick: 1-5 min
- Normal: 5-60 min
- Slow: 1-24 hours
- Very slow: > 24 hours`
              } />
            </div>
            <div className="space-y-4 text-gray-800 dark:text-gray-100">
              <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                <span className="font-medium text-gray-900 dark:text-gray-100">Your average response:</span>
                <span className="text-blue-600 dark:text-blue-300 font-bold">
                  {analysis.your_avg_response < 60 
                    ? `${analysis.your_avg_response.toFixed(1)}s`
                    : analysis.your_avg_response < 3600
                    ? `${(analysis.your_avg_response / 60).toFixed(1)}m`
                    : `${(analysis.your_avg_response / 3600).toFixed(1)}h`
                  }
                </span>
              </div>
              <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                <span className="font-medium text-gray-900 dark:text-gray-100">{friendName}'s average response:</span>
                <span className="text-green-600 dark:text-green-300 font-bold">
                  {analysis.their_avg_response < 60 
                    ? `${analysis.their_avg_response.toFixed(1)}s`
                    : analysis.their_avg_response < 3600
                    ? `${(analysis.their_avg_response / 60).toFixed(1)}m`
                    : `${(analysis.their_avg_response / 3600).toFixed(1)}h`
                  }
                </span>
              </div>
            </div>
          </motion.div>

          {/* Enhanced Analysis Sections */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            {/* Message Length Analysis */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
            >
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Message Length Analysis</h2>
              <div className="space-y-4 text-gray-800 dark:text-gray-100">
                <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">Your average length:</span>
                  <span className="text-blue-600 dark:text-blue-300 font-bold">{analysis.your_lengths?.avg_length?.toFixed(1) || 'N/A'} words</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">{friendName}'s average length:</span>
                  <span className="text-green-600 dark:text-green-300 font-bold">{analysis.their_lengths?.avg_length?.toFixed(1) || 'N/A'} words</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-purple-50 dark:bg-purple-900 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">Longest message:</span>
                  <span className="text-purple-600 dark:text-purple-300 font-bold">
                    {Math.max(analysis.your_lengths?.longest || 0, analysis.their_lengths?.longest || 0)} words
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Friendship Intensity */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
            >
              <div className="flex items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mr-2">Friendship Intensity</h2>
                <CustomTooltip text={
                  `Friendship intensity is a score (0-100) based on:
- Message volume
- Response speed
- Conversation gaps
- Balance of messages

Higher scores mean a closer, more active friendship.`
                } />
              </div>
              <div className="space-y-4 text-gray-800 dark:text-gray-100">
                <div className="flex justify-between items-center p-4 bg-purple-100 dark:bg-purple-800 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">Intensity Score:</span>
                  <span className="text-purple-600 dark:text-purple-300 font-bold text-xl">{analysis.friendship_intensity || 0}/100</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-orange-50 dark:bg-orange-900 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">Rating:</span>
                  <span className="text-orange-600 dark:text-orange-300 font-bold">{analysis.friendship_rating || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-green-50 dark:bg-green-900 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-gray-100">Messages per day:</span>
                  <span className="text-green-600 dark:text-green-300 font-bold">{analysis.messages_per_day?.toFixed(1) || 'N/A'}</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Response Time Categories */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Response Time Breakdown</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-300 mb-3">Your Response Times</h3>
                <div className="space-y-2">
                  {analysis.your_response_categories && Object.entries(analysis.your_response_categories).map(([category, data]) => (
                    <div key={category} className="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900 rounded">
                      <span className="font-medium text-gray-900 dark:text-gray-100 capitalize">{category.replace('_', ' ')}</span>
                      <span className="text-blue-600 dark:text-blue-300">{data.count} ({data.percentage.toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-green-600 dark:text-green-300 mb-3">{friendName}'s Response Times</h3>
                <div className="space-y-2">
                  {analysis.their_response_categories && Object.entries(analysis.their_response_categories).map(([category, data]) => (
                    <div key={category} className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900 rounded">
                      <span className="font-medium text-gray-900 dark:text-gray-100 capitalize">{category.replace('_', ' ')}</span>
                      <span className="text-green-600 dark:text-green-300">{data.count} ({data.percentage.toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            {/* Response Time Legend */}
            <div className="mt-6 bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-sm text-gray-700 dark:text-gray-300">
              <span className="font-semibold mr-2">Legend:</span>
              <span className="inline-block mr-4"><span className="font-bold">Instant</span>: &lt; 1 min</span>
              <span className="inline-block mr-4"><span className="font-bold">Quick</span>: 1-5 min</span>
              <span className="inline-block mr-4"><span className="font-bold">Normal</span>: 5-60 min</span>
              <span className="inline-block mr-4"><span className="font-bold">Slow</span>: 1-24 hours</span>
              <span className="inline-block"><span className="font-bold">Very slow</span>: &gt; 24 hours</span>
            </div>
          </motion.div>

          {/* Conversation Gaps */}
          {analysis.conversation_gaps && analysis.conversation_gaps.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6"
            >
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Conversation Gaps</h2>
              <p className="text-gray-600 dark:text-gray-300 mb-4">Periods of no communication (longer than 24 hours)</p>
              <div className="space-y-3">
                {analysis.conversation_gaps.slice(0, 5).map((gap, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900 rounded-lg">
                    <div>
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {new Date(gap.start).toLocaleDateString()} - {new Date(gap.end).toLocaleDateString()}
                      </span>
                    </div>
                    <span className="text-red-600 dark:text-red-300 font-bold">{gap.duration_days.toFixed(1)} days</span>
                  </div>
                ))}
                {analysis.conversation_gaps.length > 5 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
                    +{analysis.conversation_gaps.length - 5} more gaps
                  </p>
                )}
              </div>
            </motion.div>
          )}

          {/* Enhanced Shared Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Shared Content Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-300 mb-3">Your Shared Content</h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Instagram Posts</span>
                    <span className="text-blue-600 dark:text-blue-300">{(analysis.your_shared_content?.instagram_posts || 0) + (analysis.your_shared_content?.instagram_reels || 0)}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Story Replies</span>
                    <span className="text-blue-600 dark:text-blue-300">{analysis.your_shared_content?.story_replies || 0}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Other Links</span>
                    <span className="text-blue-600 dark:text-blue-300">{analysis.your_shared_content?.other_links || 0}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-green-600 dark:text-green-300 mb-3">{friendName}'s Shared Content</h3>
                <div className="space-y-2">
                  <div className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Instagram Posts</span>
                    <span className="text-green-600 dark:text-green-300">{(analysis.their_shared_content?.instagram_posts || 0) + (analysis.their_shared_content?.instagram_reels || 0)}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Story Replies</span>
                    <span className="text-green-600 dark:text-green-300">{analysis.their_shared_content?.story_replies || 0}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900 rounded">
                    <span className="font-medium text-gray-900 dark:text-gray-100">Other Links</span>
                    <span className="text-green-600 dark:text-green-300">{analysis.their_shared_content?.other_links || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Word Analysis */}
          {yourWords.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mt-6"
            >
              <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Most Used Words</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-300 mb-3">Your words</h3>
                  <div className="space-y-2">
                    {yourWords.slice(0, 10).map((word, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900 rounded">
                        <span className="font-medium text-gray-900 dark:text-gray-100">{word[0]}</span>
                        <span className="text-blue-600 dark:text-blue-300">{word[1]} times</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-green-600 dark:text-green-300 mb-3">{friendName}'s words</h3>
                  <div className="space-y-2">
                    {theirWords.slice(0, 10).map((word, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900 rounded">
                        <span className="font-medium text-gray-900 dark:text-gray-100">{word[0]}</span>
                        <span className="text-green-600 dark:text-green-300">{word[1]} times</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FriendAnalysisPage; 