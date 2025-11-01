import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, Code, Users, Award, Activity, RefreshCw } from 'lucide-react';
import { fetchAllData } from './services/api';
import './App.css';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    problems: [],
    users: [],
    submissions: [],
    analysis: {
      content_mining: {},
      structure_mining: {},
      usage_mining: {}
    }
  });

  // Load data from API
  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('🔄 Loading data from Flask API...');
      const result = await fetchAllData();

      console.log('✅ Data loaded successfully:', {
        problems: result.problems?.length,
        users: result.users?.length,
        submissions: result.submissions?.length,
        analysis: !!result.analysis
      });

      setData(result);
    } catch (err) {
      console.error('❌ Error loading data:', err);
      setError(err.message || 'Failed to load data from API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-white text-xl">Loading data from MongoDB...</p>
          <p className="text-gray-400 mt-2">Please ensure Flask server is running at http://localhost:5000</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-gray-900 flex items-center justify-center">
        <div className="text-center bg-red-900/30 p-8 rounded-lg border border-red-500 max-w-md">
          <h2 className="text-white text-2xl font-bold mb-4">❌ Connection Error</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <p className="text-gray-400 mb-2">Make sure Flask server is running:</p>
          <code className="block bg-gray-900 p-3 rounded text-sm text-left">
            cd api<br />
            python server.py
          </code>
          <button
            onClick={loadData}
            className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
          >
            <RefreshCw className="inline w-4 h-4 mr-2" />
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const stats = [
    { 
      icon: Code, 
      label: 'Total Problems', 
      value: data.problems.length, 
      color: 'bg-blue-500' 
    },
    { 
      icon: Users, 
      label: 'Active Users', 
      value: data.users.length, 
      color: 'bg-green-500' 
    },
    { 
      icon: Activity, 
      label: 'Submissions', 
      value: data.submissions.length, 
      color: 'bg-purple-500' 
    },
    { 
      icon: Award, 
      label: 'Avg Rating', 
      value: Math.round(
        data.problems.filter(p => p.rating).reduce((a, p) => a + p.rating, 0) / 
        data.problems.filter(p => p.rating).length
      ) || 0, 
      color: 'bg-orange-500' 
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Codeforces Analytics Dashboard
              </h1>
              <p className="text-gray-400">Web Mining Analysis: Content, Structure & Usage Mining</p>
              <div className="mt-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400">Connected to MongoDB</span>
              </div>
            </div>
            <button
              onClick={loadData}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Data
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <stat.icon className="w-8 h-8 text-gray-400" />
                <div className={`${stat.color} w-3 h-3 rounded-full animate-pulse`} />
              </div>
              <div className="text-3xl font-bold mb-1">{stat.value.toLocaleString()}</div>
              <div className="text-sm text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {['overview', 'content', 'structure', 'usage', 'predictions'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="space-y-6">
          {activeTab === 'overview' && <OverviewTab data={data} />}
          {activeTab === 'content' && <ContentMiningTab data={data} />}
          {activeTab === 'structure' && <StructureMiningTab data={data} />}
          {activeTab === 'usage' && <UsageMiningTab data={data} />}
          {activeTab === 'predictions' && <PredictionsTab data={data} />}
        </div>
      </div>
    </div>
  );
}

// ============= TAB COMPONENTS =============

const OverviewTab = ({ data }) => {
  const ratingDist = data.problems.reduce((acc, p) => {
    if (!p.rating) return acc;
    const rating = Math.floor(p.rating / 100) * 100;
    acc[rating] = (acc[rating] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(ratingDist)
    .map(([rating, count]) => ({ rating: parseInt(rating), count }))
    .sort((a, b) => a.rating - b.rating);

  // Top languages
  const langCounts = data.submissions.reduce((acc, s) => {
    if (s.programming_language) {
      acc[s.programming_language] = (acc[s.programming_language] || 0) + 1;
    }
    return acc;
  }, {});

  const topLanguages = Object.entries(langCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  const maxLangCount = topLanguages[0]?.count || 1;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Rating Distribution" icon={TrendingUp}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="rating" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} 
            />
            <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Top Programming Languages" icon={Code}>
        <div className="space-y-3">
          {topLanguages.map((lang, idx) => (
            <div key={idx} className="flex items-center">
              <div className="flex-1">
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium truncate">{lang.name}</span>
                  <span className="text-sm text-gray-400 ml-2">{lang.count}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${(lang.count / maxLangCount) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </ChartCard>
    </div>
  );
};

const ContentMiningTab = ({ data }) => {
  const tagCounts = {};
  data.problems.forEach(p => {
    if (Array.isArray(p.tags)) {
      p.tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    }
  });

  const tagData = Object.entries(tagCounts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Top Problem Tags" icon={Activity}>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={tagData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              dataKey="value"
            >
              {tagData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Tag Distribution" icon={Activity}>
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {Object.entries(tagCounts).sort((a, b) => b[1] - a[1]).slice(0, 15).map(([tag, count]) => {
            const maxCount = Object.values(tagCounts).sort((a, b) => b - a)[0];
            return (
              <div key={tag} className="flex items-center">
                <div className="w-32 text-sm truncate">{tag}</div>
                <div className="flex-1 ml-3">
                  <div className="w-full bg-gray-700 rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full"
                      style={{ width: `${(count / maxCount) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="w-12 text-right text-sm ml-3">{count}</div>
              </div>
            );
          })}
        </div>
      </ChartCard>
    </div>
  );
};

const StructureMiningTab = ({ data }) => {
  const contestCount = new Set(data.problems.map(p => p.contest_id)).size;
  const avgProblemsPerContest = (data.problems.length / contestCount).toFixed(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Total Contests</h3>
        <div className="text-4xl font-bold text-blue-400">{contestCount}</div>
      </div>
      <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Avg Problems/Contest</h3>
        <div className="text-4xl font-bold text-green-400">{avgProblemsPerContest}</div>
      </div>
      <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">Total Problems</h3>
        <div className="text-4xl font-bold text-purple-400">{data.problems.length}</div>
      </div>
    </div>
  );
};

const UsageMiningTab = ({ data }) => {
  const verdictCounts = data.submissions.reduce((acc, s) => {
    acc[s.verdict] = (acc[s.verdict] || 0) + 1;
    return acc;
  }, {});

  const verdictData = Object.entries(verdictCounts)
    .map(([verdict, count]) => ({ verdict: verdict.slice(0, 15), count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  const acceptanceRate = ((verdictCounts['OK'] || 0) / data.submissions.length * 100).toFixed(1);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Verdict Distribution" icon={Activity}>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={verdictData}
              cx="50%"
              cy="50%"
              outerRadius={80}
              dataKey="count"
              label={({ verdict }) => verdict}
            >
              {verdictData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Submission Statistics" icon={Activity}>
        <div className="space-y-4">
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Total Submissions</div>
            <div className="text-3xl font-bold text-blue-400">{data.submissions.length.toLocaleString()}</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Acceptance Rate</div>
            <div className="text-3xl font-bold text-green-400">{acceptanceRate}%</div>
          </div>
          <div className="bg-gray-700/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Active Users</div>
            <div className="text-3xl font-bold text-purple-400">{data.users.length}</div>
          </div>
        </div>
      </ChartCard>
    </div>
  );
};

const PredictionsTab = ({ data }) => {
  const predicted = data.problems.filter(p => p.predicted_rating && !p.rating);
  const withRating = data.problems.filter(p => p.rating);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6">
          <div className="text-blue-200 text-sm mb-2">Problems Predicted</div>
          <div className="text-4xl font-bold">{predicted.length}</div>
        </div>
        <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6">
          <div className="text-green-200 text-sm mb-2">With Actual Rating</div>
          <div className="text-4xl font-bold">{withRating.length}</div>
        </div>
        <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6">
          <div className="text-purple-200 text-sm mb-2">Total Problems</div>
          <div className="text-4xl font-bold">{data.problems.length}</div>
        </div>
      </div>

      <ChartCard title="Sample Predicted Problems" icon={Code}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-4 py-3 text-left">Problem ID</th>
                <th className="px-4 py-3 text-left">Title</th>
                <th className="px-4 py-3 text-left">Tags</th>
                <th className="px-4 py-3 text-right">Predicted Rating</th>
              </tr>
            </thead>
            <tbody>
              {predicted.slice(0, 10).map((p, idx) => (
                <tr key={idx} className="border-t border-gray-700 hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-mono">{p.problem_id}</td>
                  <td className="px-4 py-3 truncate max-w-xs">{p.title}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(p.tags || []).slice(0, 2).map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right font-bold text-blue-400">{p.predicted_rating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartCard>
    </div>
  );
};

const ChartCard = ({ title, icon: Icon, children }) => (
  <div className="bg-gray-800/50 backdrop-blur rounded-lg p-6 border border-gray-700">
    <div className="flex items-center mb-4">
      {Icon && <Icon className="w-5 h-5 text-blue-400 mr-2" />}
      <h3 className="text-lg font-semibold">{title}</h3>
    </div>
    {children}
  </div>
);

export default App;