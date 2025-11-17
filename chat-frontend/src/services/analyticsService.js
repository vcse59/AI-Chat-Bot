import axios from 'axios';
import authService from './authService';

const ANALYTICS_API_URL = process.env.REACT_APP_ANALYTICS_API_URL || 'http://localhost:8002';

class AnalyticsService {
  /**
   * Get overall analytics summary
   * @returns {Promise} - Returns analytics summary
   */
  async getSummary() {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/summary`, {
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get user activities with pagination
   * @param {number} skip - Number of records to skip
   * @param {number} limit - Maximum number of records to return
   * @returns {Promise} - Returns user activities
   */
  async getUserActivities(skip = 0, limit = 50) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/users/activities`, {
        params: { skip, limit },
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get top active users
   * @param {number} limit - Maximum number of users to return
   * @returns {Promise} - Returns top users
   */
  async getTopUsers(limit = 10) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/users/top`, {
        params: { limit },
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get conversation metrics
   * @param {object} params - Query parameters (start_date, end_date, user_id)
   * @returns {Promise} - Returns conversation metrics
   */
  async getConversationMetrics(params = {}) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/conversations`, {
        params,
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get API usage statistics
   * @param {object} params - Query parameters (start_date, end_date, endpoint)
   * @returns {Promise} - Returns API usage data
   */
  async getAPIUsage(params = {}) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/api-usage`, {
        params,
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get daily statistics
   * @param {object} params - Query parameters (start_date, end_date)
   * @returns {Promise} - Returns daily statistics
   */
  async getDailyStats(params = {}) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/daily-stats`, {
        params,
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Track user activity manually
   * @param {object} activityData - Activity data to track
   * @returns {Promise} - Returns created activity
   */
  async trackActivity(activityData) {
    try {
      const response = await axios.post(
        `${ANALYTICS_API_URL}/api/v1/analytics/track/activity`,
        activityData,
        {
          headers: authService.getAuthHeader(),
        }
      );
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Check if current user has admin access
   * @returns {Promise<boolean>} - Returns true if user is admin
   */
  async checkAdminAccess() {
    try {
      // Try to access summary endpoint - only admins can access
      await this.getSummary();
      return true;
    } catch (error) {
      if (error.message && error.message.includes('403')) {
        return false;
      }
      throw error;
    }
  }

  /**
   * Get user metrics grouped by role
   * @returns {Promise} - Returns metrics by role
   */
  async getMetricsByRole() {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/metrics/by-role`, {
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get detailed metrics for users
   * @param {string} userId - Optional user ID to filter
   * @param {number} limit - Maximum number of users
   * @returns {Promise} - Returns detailed user metrics
   */
  async getUsersDetailedMetrics(userId = null, limit = 100) {
    try {
      const params = { limit };
      if (userId) params.user_id = userId;
      
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/users/detailed-metrics`, {
        params,
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get conversations for a specific user
   * @param {string} userId - User ID
   * @param {number} limit - Maximum number of conversations
   * @returns {Promise} - Returns user's conversations with metrics
   */
  async getUserConversations(userId, limit = 50) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/users/${userId}/conversations`, {
        params: { limit },
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get detailed metrics for a specific conversation
   * @param {string} conversationId - Conversation ID
   * @returns {Promise} - Returns conversation details with all messages
   */
  async getConversationDetailed(conversationId) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/conversations/${conversationId}/detailed`, {
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get token usage by conversation
   * @param {string} userId - Optional user ID to filter
   * @param {number} limit - Maximum number of conversations
   * @returns {Promise} - Returns token usage breakdown
   */
  async getTokenUsageByConversation(userId = null, limit = 50) {
    try {
      const params = { limit };
      if (userId) params.user_id = userId;
      
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/tokens/by-conversation`, {
        params,
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get response times by user
   * @param {number} limit - Maximum number of users
   * @returns {Promise} - Returns response time statistics
   */
  async getResponseTimesByUser(limit = 50) {
    try {
      const response = await axios.get(`${ANALYTICS_API_URL}/api/v1/analytics/response-times/by-user`, {
        params: { limit },
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Clear all analytics data (Admin only)
   * @returns {Promise} - Returns confirmation of cleared data
   */
  async clearAllStats() {
    try {
      const response = await axios.delete(`${ANALYTICS_API_URL}/api/v1/analytics/clear-all`, {
        headers: authService.getAuthHeader(),
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Handle API errors
   * @private
   */
  _handleError(error) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      
      if (status === 403) {
        return new Error('Admin access required. You do not have permission to access analytics.');
      } else if (status === 401) {
        return new Error('Authentication required. Please login again.');
      }
      
      return new Error(message);
    } else if (error.request) {
      // No response received
      return new Error('No response from analytics service. Please check your connection.');
    } else {
      // Request setup error
      return new Error(error.message || 'An error occurred');
    }
  }
}

export default new AnalyticsService();
