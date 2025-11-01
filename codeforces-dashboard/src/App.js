import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter
} from 'recharts';
import { TrendingUp, Code, Users, Award, Activity, RefreshCw, Network, Zap, Target, Clock } from 'lucide-react';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5000/api/data');
      if (!response.ok) throw new Error('Failed to fetch data');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-white text-xl">Loading analysis data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-gray-900 flex items-center justify-center">
        <div className="text-center bg-red-900/30 p-8 rounded-lg border border-red-500 max-w-md">
          <h2 className="text-white text-2xl font-bold mb-4">Connection Error</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium"
          >
            <RefreshCw className="inline w-4 h-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  const analysis = data.analysis || {};
  const contentMining = analysis.content_mining || {};
  const structureMining = analysis.structure_mining || {};
  const usageMining = analysis.usage_mining || {};

  const stats = [
    { icon: Code, label: 'Total Problems', value: data.problems.length, color: 'bg-blue-500' },
    { icon: Users, label: 'Active Users', value: data.users.length, color: 'bg-green-500' },
    { icon: Activity, label: 'Submissions', value: data.submissions.length, color: 'bg-purple-500' },
    { icon: Award, label: 'Avg Rating', value: Math.round(contentMining.avg_title_length || 0), color: 'bg-orange-500' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Codeforces Web Mining Dashboard
              </h1>
              <p className="text-gray-400">Complete Analysis: Content, Structure & Usage Mining</p>
              <div className="mt-2 flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-400">MongoDB Connected</span>
              </div>
            </div>
            <button onClick={loadData} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

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

        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {['overview', 'content', 'structure', 'usage', 'predictor'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50'
              }`}
            >
              {tab === 'predictor' ? 'Rating Predictor' : tab.charAt(0).toUpperCase() + tab.slice(1) + ' Mining'}
            </button>
          ))}
        </div>

        <div className="space-y-6">
          {activeTab === 'overview' && <OverviewTab data={data} analysis={analysis} />}
          {activeTab === 'content' && <ContentMiningTab contentMining={contentMining} />}
          {activeTab === 'structure' && <StructureMiningTab structureMining={structureMining} />}
          {activeTab === 'usage' && <UsageMiningTab usageMining={usageMining} />}
          {activeTab === 'predictor' && <RatingPredictorTab problems={data.problems} />}
        </div>
      </div>
    </div>
  );
}

const OverviewTab = ({ data, analysis }) => {
  const contentMining = analysis.content_mining || {};
  const ratingDist = contentMining.rating_distribution || {};
  
  const chartData = Object.entries(ratingDist)
    .map(([rating, count]) => ({ rating: parseInt(rating), count }))
    .sort((a, b) => a.rating - b.rating);

  const topTags = (contentMining.top_tags || []).slice(0, 10);
  const tagData = topTags.map(([name, value]) => ({ name, value }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChartCard title="Rating Distribution" icon={TrendingUp}>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="rating" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
            <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Top Problem Tags" icon={Activity}>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={tagData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name.slice(0, 10)}: ${(percent * 100).toFixed(0)}%`}
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
    </div>
  );
};

const ContentMiningTab = ({ contentMining }) => {
  const topTags = (contentMining.top_tags || []).slice(0, 15);
  const maxCount = topTags[0]?.[1] || 1;
  const clusters = contentMining.clusters || {};

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Unique Tags" value={topTags.length} color="blue" />
        <StatCard title="Avg Title Length" value={Math.round(contentMining.avg_title_length || 0)} color="green" />
        <StatCard title="Topic Clusters" value={Object.keys(clusters).length} color="purple" />
      </div>

      <ChartCard title="Tag Distribution Analysis" icon={Activity}>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {topTags.map(([tag, count], idx) => (
            <div key={idx} className="flex items-center">
              <div className="w-40 text-sm font-medium truncate">{tag}</div>
              <div className="flex-1 ml-3">
                <div className="w-full bg-gray-700 rounded-full h-4">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  />
                </div>
              </div>
              <div className="w-16 text-right text-sm ml-3 font-bold">{count}</div>
            </div>
          ))}
        </div>
      </ChartCard>

      {Object.keys(clusters).length > 0 && (
        <ChartCard title="Problem Clusters by Topics" icon={Network}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(clusters).map(([clusterId, tags]) => (
              <div key={clusterId} className="bg-gray-700/30 rounded-lg p-4">
                <h4 className="text-lg font-semibold mb-3 text-blue-400">Cluster {clusterId}</h4>
                <div className="space-y-2">
                  {tags.map(([tag, count], idx) => (
                    <div key={idx} className="flex justify-between items-center">
                      <span className="text-sm truncate">{tag}</span>
                      <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ChartCard>
      )}
    </div>
  );
};

const StructureMiningTab = ({ structureMining }) => {
  const topPairs = (structureMining.top_tag_pairs || []).slice(0, 15);
  const maxPairCount = topPairs[0]?.[1] || 1;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Total Contests" value={structureMining.total_contests || 0} color="blue" />
        <StatCard title="Avg Problems/Contest" value={(structureMining.avg_problems_per_contest || 0).toFixed(1)} color="green" />
        <StatCard title="Progressive Contests" value={`${(structureMining.progressive_contests_pct || 0).toFixed(1)}%`} color="purple" />
      </div>

      <ChartCard title="Tag Co-occurrence Network" icon={Network}>
        <p className="text-sm text-gray-400 mb-4">Tags that frequently appear together in problems</p>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {topPairs.map(([[tag1, tag2], count], idx) => (
            <div key={idx} className="flex items-center">
              <div className="flex-1 text-sm">
                <span className="text-blue-400">{tag1}</span>
                <span className="text-gray-500 mx-2">↔</span>
                <span className="text-purple-400">{tag2}</span>
              </div>
              <div className="w-48 ml-3">
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full"
                    style={{ width: `${(count / maxPairCount) * 100}%` }}
                  />
                </div>
              </div>
              <div className="w-12 text-right text-sm ml-3 font-bold">{count}</div>
            </div>
          ))}
        </div>
      </ChartCard>

      {structureMining.problem_index_distribution && (
        <ChartCard title="Problem Index Distribution" icon={Target}>
          <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
            {Object.entries(structureMining.problem_index_distribution).map(([index, count]) => (
              <div key={index} className="bg-gray-700/30 rounded-lg p-3 text-center">
                <div className="text-2xl font-bold text-blue-400">{index}</div>
                <div className="text-xs text-gray-400 mt-1">{count} problems</div>
              </div>
            ))}
          </div>
        </ChartCard>
      )}
    </div>
  );
};

const UsageMiningTab = ({ usageMining }) => {
  const topLanguages = Object.entries(usageMining.top_languages || {}).slice(0, 10);
  const langSuccess = usageMining.language_success_rates || {};
  const verdictDist = usageMining.verdict_distribution || {};

  const langSuccessData = Object.entries(langSuccess)
    .map(([name, rate]) => ({ name: name.slice(0, 15), rate: parseFloat(rate.toFixed(1)) }))
    .sort((a, b) => b.rate - a.rate);

  const verdictData = Object.entries(verdictDist)
    .map(([verdict, count]) => ({ verdict: verdict.slice(0, 15), count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Acceptance Rate" value={`${(usageMining.acceptance_rate || 0).toFixed(1)}%`} color="green" />
        <StatCard title="Avg Time (ms)" value={Math.round(usageMining.avg_time_millis || 0)} color="blue" />
        <StatCard title="Avg Memory (MB)" value={(usageMining.avg_memory_bytes / 1024 / 1024 || 0).toFixed(1)} color="purple" />
        <StatCard title="Avg Submissions/User" value={(usageMining.avg_submissions_per_user || 0).toFixed(0)} color="orange" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Language Success Rates" icon={Award}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={langSuccessData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9ca3af" />
              <YAxis dataKey="name" type="category" width={100} stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
              <Bar dataKey="rate" fill="#10b981" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

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
      </div>

      <ChartCard title="Top Programming Languages" icon={Code}>
        <div className="space-y-3">
          {topLanguages.map(([lang, count], idx) => {
            const maxCount = topLanguages[0]?.[1] || 1;
            const successRate = langSuccess[lang] || 0;
            return (
              <div key={idx} className="flex items-center">
                <div className="w-40 text-sm font-medium truncate">{lang}</div>
                <div className="flex-1 ml-3">
                  <div className="w-full bg-gray-700 rounded-full h-4">
                    <div
                      className="bg-blue-500 h-4 rounded-full transition-all"
                      style={{ width: `${(count / maxCount) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="w-20 text-right text-sm ml-3">
                  <span className="font-bold">{count}</span>
                  <span className="text-green-400 ml-2 text-xs">({successRate.toFixed(1)}%)</span>
                </div>
              </div>
            );
          })}
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

const StatCard = ({ title, value, color }) => {
  const colors = {
    blue: 'from-blue-600 to-blue-800',
    green: 'from-green-600 to-green-800',
    purple: 'from-purple-600 to-purple-800',
    orange: 'from-orange-600 to-orange-800'
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-lg p-6`}>
      <div className="text-sm text-gray-200 mb-2">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
};

const RatingPredictorTab = ({ problems }) => {
  // Phân loại problems
  const withRating = problems.filter(p => p.rating && !p.predicted_rating);
  const predicted = problems.filter(p => p.predicted_rating && !p.rating);
  const both = problems.filter(p => p.rating && p.predicted_rating);
  
  // Statistics
  const avgActual = withRating.length > 0 
    ? (withRating.reduce((sum, p) => sum + p.rating, 0) / withRating.length).toFixed(0)
    : 0;
    
  const avgPredicted = predicted.length > 0
    ? (predicted.reduce((sum, p) => sum + p.predicted_rating, 0) / predicted.length).toFixed(0)
    : 0;

  // Rating distribution for predicted
  const predictedDist = predicted.reduce((acc, p) => {
    const rating = Math.floor(p.predicted_rating / 100) * 100;
    acc[rating] = (acc[rating] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(predictedDist)
    .map(([rating, count]) => ({ rating: parseInt(rating), count }))
    .sort((a, b) => a.rating - b.rating);

  // Model accuracy (nếu có cả actual và predicted)
  let accuracy = null;
  if (both.length > 0) {
    const mae = both.reduce((sum, p) => sum + Math.abs(p.rating - p.predicted_rating), 0) / both.length;
    accuracy = mae.toFixed(0);
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Problems with Actual Rating" value={withRating.length} color="blue" />
        <StatCard title="Problems with Predicted Rating" value={predicted.length} color="green" />
        <StatCard title="Avg Predicted Rating" value={avgPredicted} color="purple" />
        {accuracy && <StatCard title="Model MAE" value={`±${accuracy}`} color="orange" />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Predicted Rating Distribution */}
        <ChartCard title="Predicted Rating Distribution" icon={TrendingUp}>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="rating" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Model Info */}
        <ChartCard title="Prediction Model Info" icon={Zap}>
          <div className="space-y-4">
            <div className="bg-gray-700/30 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Model Type</div>
              <div className="text-lg font-bold">Random Forest Regressor</div>
            </div>
            <div className="bg-gray-700/30 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Features Used</div>
              <div className="text-sm">
                <span className="inline-block bg-blue-500/20 text-blue-300 px-2 py-1 rounded mr-2 mb-1">Tags</span>
                <span className="inline-block bg-green-500/20 text-green-300 px-2 py-1 rounded mr-2 mb-1">Solved Count</span>
                <span className="inline-block bg-purple-500/20 text-purple-300 px-2 py-1 rounded mr-2 mb-1">Index Position</span>
                <span className="inline-block bg-orange-500/20 text-orange-300 px-2 py-1 rounded mb-1">Title Length</span>
              </div>
            </div>
            <div className="bg-gray-700/30 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Training Set</div>
              <div className="text-lg font-bold">{withRating.length} problems</div>
            </div>
          </div>
        </ChartCard>
      </div>

      {/* Sample Predicted Problems */}
      <ChartCard title="Sample Predicted Problems (Without Actual Rating)" icon={Target}>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-4 py-3 text-left">Contest ID</th>
                <th className="px-4 py-3 text-left">Index</th>
                <th className="px-4 py-3 text-left">Title</th>
                <th className="px-4 py-3 text-left">Tags</th>
                <th className="px-4 py-3 text-center">Solved</th>
                <th className="px-4 py-3 text-right">Predicted Rating</th>
              </tr>
            </thead>
            <tbody>
              {predicted.slice(0, 15).map((p, idx) => (
                <tr key={idx} className="border-t border-gray-700 hover:bg-gray-700/30">
                  <td className="px-4 py-3 font-mono text-blue-400">{p.contest_id}</td>
                  <td className="px-4 py-3 font-bold text-purple-400">{p.index}</td>
                  <td className="px-4 py-3 truncate max-w-xs" title={p.title}>{p.title}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(p.tags || []).slice(0, 2).map((tag, i) => (
                        <span key={i} className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                      {(p.tags || []).length > 2 && (
                        <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-xs">
                          +{(p.tags || []).length - 2}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center text-gray-400">{p.solved_count || 0}</td>
                  <td className="px-4 py-3 text-right">
                    <span className="font-bold text-green-400 text-lg">{p.predicted_rating}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {predicted.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <Target className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No predicted ratings found.</p>
            <p className="text-sm mt-1">Run <code className="bg-gray-700 px-2 py-1 rounded">python rating_predictor.py</code> to generate predictions.</p>
          </div>
        )}
      </ChartCard>

      {/* Comparison (if available) */}
      {both.length > 0 && (
        <ChartCard title="Model Accuracy - Actual vs Predicted" icon={Activity}>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {both.slice(0, 10).map((p, idx) => {
              const diff = p.predicted_rating - p.rating;
              const diffPercent = ((Math.abs(diff) / p.rating) * 100).toFixed(1);
              const isAccurate = Math.abs(diff) <= 100;
              
              return (
                <div key={idx} className="bg-gray-700/30 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="font-medium truncate">{p.title}</div>
                      <div className="text-xs text-gray-400">{p.contest_id}{p.index}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                      <div className="text-gray-400 text-xs">Actual</div>
                      <div className="font-bold text-blue-400">{p.rating}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Predicted</div>
                      <div className="font-bold text-green-400">{p.predicted_rating}</div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">Difference</div>
                      <div className={`font-bold ${isAccurate ? 'text-green-400' : 'text-orange-400'}`}>
                        {diff > 0 ? '+' : ''}{diff} ({diffPercent}%)
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ChartCard>
      )}
    </div>
  );
};

export default App;