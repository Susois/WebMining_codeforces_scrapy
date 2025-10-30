import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    return Promise.reject(error);
  }
);

// API methods
export const fetchProblems = async () => {
  try {
    const response = await api.get('/problems');
    return response.data;
  } catch (error) {
    console.error('Error fetching problems:', error);
    throw error;
  }
};

export const fetchUsers = async () => {
  try {
    const response = await api.get('/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const fetchSubmissions = async () => {
  try {
    const response = await api.get('/submissions');
    return response.data;
  } catch (error) {
    console.error('Error fetching submissions:', error);
    throw error;
  }
};

export const fetchAnalysis = async () => {
  try {
    const response = await api.get('/analysis');
    return response.data;
  } catch (error) {
    console.error('Error fetching analysis:', error);
    throw error;
  }
};

export const fetchAllData = async () => {
  try {
    const [problems, users, submissions, analysis] = await Promise.all([
      fetchProblems(),
      fetchUsers(),
      fetchSubmissions(),
      fetchAnalysis()
    ]);

    return {
      problems,
      users,
      submissions,
      analysis
    };
  } catch (error) {
    console.error('Error fetching all data:', error);
    throw error;
  }
};

export default api;