import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds (tăng timeout cho queries lớn)
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor
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

// Response interceptor
api.interceptors.response.use(
    (response) => {
        const dataLength = Array.isArray(response.data) ? response.data.length : 'N/A';
        console.log(`✅ API Response: ${response.config.url} (${dataLength} items)`);
        return response;
    },
    (error) => {
        console.error('❌ API Response Error:', error.message);
        return Promise.reject(error);
    }
);

// ==================== API METHODS ====================

/**
 * Fetch problems (all or limited)
 */
export const fetchProblems = async(limit = null) => {
    try {
        const params = limit ? { limit } : {};
        const response = await api.get('/problems', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching problems:', error);
        throw error;
    }
};

/**
 * Fetch users (all or limited)
 */
export const fetchUsers = async(limit = null) => {
    try {
        const params = limit ? { limit } : {};
        const response = await api.get('/users', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching users:', error);
        throw error;
    }
};

/**
 * Fetch submissions
 * @param {Object} options - { all: boolean, limit: number }
 */
export const fetchSubmissions = async(options = {}) => {
    try {
        const params = {};

        if (options.all) {
            params.all = 'true';
            console.warn('⚠️ Fetching ALL submissions - this may take time...');
        } else if (options.limit) {
            params.limit = options.limit;
        }

        const response = await api.get('/submissions', { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching submissions:', error);
        throw error;
    }
};

/**
 * Fetch submission statistics (FAST - aggregated data)
 * Sử dụng endpoint này thay vì fetch all submissions
 */
export const fetchSubmissionStats = async() => {
    try {
        const response = await api.get('/submissions/stats');
        return response.data;
    } catch (error) {
        console.error('Error fetching submission stats:', error);
        throw error;
    }
};

/**
 * Fetch analysis report
 */
export const fetchAnalysis = async() => {
    try {
        const response = await api.get('/analysis');
        return response.data;
    } catch (error) {
        console.error('Error fetching analysis:', error);
        throw error;
    }
};

/**
 * Fetch overall statistics (counts only - very fast)
 */
export const fetchStats = async() => {
    try {
        const response = await api.get('/stats');
        return response.data;
    } catch (error) {
        console.error('Error fetching stats:', error);
        throw error;
    }
};

/**
 * Health check
 */
export const healthCheck = async() => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error('Error in health check:', error);
        throw error;
    }
};

/**
 * Fetch all data (optimized version)
 * Options:
 * - fastMode: true = use stats instead of full data (default)
 * - submissionsLimit: number of submissions to fetch
 */
export const fetchAllData = async(options = {}) => {
    const { fastMode = true, submissionsLimit = 100000 } = options;

    try {
        console.log('🚀 Loading data...', { fastMode, submissionsLimit });

        if (fastMode) {
            // FAST MODE: Use aggregated stats + limited submissions
            const [problems, users, submissionStats, analysis, stats] = await Promise.all([
                fetchProblems(),
                fetchUsers(),
                fetchSubmissionStats(), // Use stats instead of full data
                fetchAnalysis(),
                fetchStats()
            ]);

            // Create pseudo submissions for charts (from stats)
            const pseudoSubmissions = createPseudoSubmissions(submissionStats);

            return {
                problems,
                users,
                submissions: pseudoSubmissions,
                submissionStats,
                analysis,
                stats
            };
        } else {
            // FULL MODE: Fetch actual submissions (slower)
            const [problems, users, submissions, analysis] = await Promise.all([
                fetchProblems(),
                fetchUsers(),
                fetchSubmissions({ limit: submissionsLimit }),
                fetchAnalysis()
            ]);

            return {
                problems,
                users,
                submissions,
                analysis
            };
        }
    } catch (error) {
        console.error('Error fetching all data:', error);
        throw error;
    }
};

/**
 * Create pseudo submissions from aggregated stats
 * Để charts vẫn hoạt động mà không cần load full data
 */
function createPseudoSubmissions(stats) {
    const submissions = [];

    // Create pseudo submissions from verdict distribution
    if (stats.verdict_distribution) {
        Object.entries(stats.verdict_distribution).forEach(([verdict, count]) => {
            // Tạo một vài pseudo submissions cho mỗi verdict
            const sampleSize = Math.min(count, 100);
            for (let i = 0; i < sampleSize; i++) {
                submissions.push({
                    verdict,
                    programming_language: 'Unknown',
                    _pseudo: true
                });
            }
        });
    }

    // Add language info from stats
    if (stats.language_distribution) {
        let idx = 0;
        Object.entries(stats.language_distribution).forEach(([lang, count]) => {
            const sampleSize = Math.min(count, 100);
            for (let i = 0; i < sampleSize && idx < submissions.length; i++, idx++) {
                submissions[idx].programming_language = lang;
            }
        });
    }

    return submissions;
}

export default api;