import axios from 'axios';
import authService from './authService';

const CHAT_API_URL = process.env.REACT_APP_CHAT_API_URL || 'http://localhost:8000';

class ChatService {
  /**
   * Get axios instance with authentication headers
   * @private
   */
  _getAxiosInstance() {
    return axios.create({
      baseURL: CHAT_API_URL,
      headers: authService.getAuthHeader(),
    });
  }

  /**
   * Get all conversations for the current user
   * @returns {Promise} - Returns array of conversations
   */
  async getConversations() {
    try {
      const api = this._getAxiosInstance();
      const currentUser = authService.getCurrentUser();
      if (!currentUser || !currentUser.username) {
        throw new Error('User not authenticated');
      }
      const response = await api.get(`/api/v1/users/${currentUser.username}/conversations/`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get a specific conversation by ID
   * @param {string} conversationId - Conversation hash ID
   * @returns {Promise} - Returns conversation data
   */
  async getConversation(conversationId) {
    try {
      const api = this._getAxiosInstance();
      const currentUser = authService.getCurrentUser();
      if (!currentUser || !currentUser.username) {
        throw new Error('User not authenticated');
      }
      const response = await api.get(`/api/v1/users/${currentUser.username}/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Create a new conversation
   * @param {string} title - Conversation title
   * @returns {Promise} - Returns created conversation
   */
  async createConversation(title) {
    try {
      const api = this._getAxiosInstance();
      const currentUser = authService.getCurrentUser();
      if (!currentUser || !currentUser.username) {
        throw new Error('User not authenticated');
      }
      const response = await api.post(`/api/v1/users/${currentUser.username}/conversations/`, { 
        title,
        user_id: currentUser.username 
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Update a conversation
   * @param {string} conversationId - Conversation hash ID
   * @param {object} data - Update data (e.g., {title: "New Title"})
   * @returns {Promise} - Returns updated conversation
   */
  async updateConversation(conversationId, data) {
    try {
      const api = this._getAxiosInstance();
      const currentUser = authService.getCurrentUser();
      if (!currentUser || !currentUser.username) {
        throw new Error('User not authenticated');
      }
      const response = await api.put(`/api/v1/users/${currentUser.username}/conversations/${conversationId}`, data);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Delete a conversation
   * @param {string} conversationId - Conversation hash ID
   * @returns {Promise}
   */
  async deleteConversation(conversationId) {
    try {
      const api = this._getAxiosInstance();
      const currentUser = authService.getCurrentUser();
      if (!currentUser || !currentUser.username) {
        throw new Error('User not authenticated');
      }
      await api.delete(`/api/v1/users/${currentUser.username}/conversations/${conversationId}`);
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get all messages in a conversation
   * @param {string} conversationId - Conversation hash ID
   * @returns {Promise} - Returns array of messages
   */
  async getMessages(conversationId) {
    try {
      const api = this._getAxiosInstance();
      const response = await api.get(`/api/v1/conversations/${conversationId}/messages/`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Send a message in a conversation
   * @param {string} conversationId - Conversation hash ID
   * @param {string} content - Message content
   * @param {string} role - Message role (user/assistant)
   * @returns {Promise} - Returns created message
   */
  async sendMessage(conversationId, content, role = 'user') {
    try {
      const api = this._getAxiosInstance();
      const response = await api.post(`/api/v1/conversations/${conversationId}/messages/`, {
        conversation_id: conversationId,
        role: role,
        content: content,
      });
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Get a specific message by ID
   * @param {string} messageId - Message hash ID
   * @returns {Promise} - Returns message data
   */
  async getMessage(messageId) {
    try {
      const api = this._getAxiosInstance();
      const response = await api.get(`/messages/${messageId}`);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Update a message
   * @param {string} messageId - Message hash ID
   * @param {object} data - Update data
   * @returns {Promise} - Returns updated message
   */
  async updateMessage(messageId, data) {
    try {
      const api = this._getAxiosInstance();
      const response = await api.put(`/messages/${messageId}`, data);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Delete a message
   * @param {string} messageId - Message hash ID
   * @returns {Promise}
   */
  async deleteMessage(messageId) {
    try {
      const api = this._getAxiosInstance();
      await api.delete(`/messages/${messageId}`);
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Admin: Get all conversations from all users
   * @returns {Promise} - Returns array of all conversations
   */
  async getAllConversationsAdmin() {
    try {
      const api = this._getAxiosInstance();
      const response = await api.get('/api/v1/admin/conversations/');
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Admin: Delete any conversation
   * @param {string} conversationId - Conversation hash ID
   * @returns {Promise}
   */
  async deleteConversationAdmin(conversationId) {
    try {
      const api = this._getAxiosInstance();
      await api.delete(`/api/v1/admin/conversations/${conversationId}`);
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Admin: Delete a user and all their data
   * @param {string} username - Username to delete
   * @returns {Promise}
   */
  async deleteUserAdmin(username) {
    try {
      const api = this._getAxiosInstance();
      const response = await api.delete(`/api/v1/admin/users/${username}`);
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
      // Handle 401 Unauthorized - redirect to login
      if (error.response.status === 401) {
        authService.logout();
        window.location.href = '/login';
        return new Error('Session expired. Please login again.');
      }
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return new Error(message);
    } else if (error.request) {
      return new Error('No response from server. Please check your connection.');
    } else {
      return new Error(error.message || 'An error occurred');
    }
  }
}

export default new ChatService();
