// services/api.js
const API_BASE_URL = 'http://localhost:5000/api';

// Increased timeout for large datasets (5 minutes)
const FETCH_TIMEOUT = 300000; // 300 seconds = 5 minutes

/**
 * Fetch with timeout support
 */
const fetchWithTimeout = async(url, options = {}, timeout = FETCH_TIMEOUT) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error(`Request timeout after ${timeout / 1000}s. The dataset might be too large.`);
        }
        throw error;
    }
};

/**
 * Fetch all data for dashboard including analysis report
 */
export const fetchAllData = async() => {
    try {
        console.log('🔄 Fetching data from Flask API...');
        console.log('⏱️  This may take 30-120 seconds for large datasets...');

        const startTime = Date.now();
        const response = await fetchWithTimeout(`${API_BASE_URL}/data`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const loadTime = ((Date.now() - startTime) / 1000).toFixed(2);

        if (data.status === 'error') {
            throw new Error(data.error || 'Unknown error');
        }

        console.log(`✅ Data loaded successfully in ${loadTime}s:`, {
            problems: data.problems ? .length || 0,
            users: data.users ? .length || 0,
            submissions: data.submissions ? .length || 0,
            hasAnalysis: !!data.analysis ? .content_mining
        });

        return data;
    } catch (error) {
        console.error('❌ Error fetching data:', error);
        throw error;
    }
};

/**
 * Fetch only analysis report (faster for refresh)
 */
export const fetchAnalysisOnly = async() => {
    try {
        console.log('📊 Fetching analysis report...');
        const response = await fetchWithTimeout(`${API_BASE_URL}/analysis`, {}, 30000); // 30s timeout

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'error') {
            console.warn('⚠️ No analysis report found:', data.message);
            return data.analysis; // Return empty structure
        }

        console.log('✅ Analysis loaded');
        return data.analysis;
    } catch (error) {
        console.error('❌ Error fetching analysis:', error);
        throw error;
    }
};

/**
 * Health check
 */
export const checkHealth = async() => {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 10000); // 10s timeout
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Health check failed:', error);
        throw error;
    }
};

/**
 * Get quick stats (faster than full data)
 */
export const fetchStats = async() => {
    try {
        const response = await fetchWithTimeout(`${API_BASE_URL}/stats`, {}, 30000); // 30s timeout
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('❌ Error fetching stats:', error);
        throw error;
    }
};