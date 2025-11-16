import axios from 'axios';

const AUTH_API_URL = process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8001';

class AuthService {
  /**
   * Login with username and password
   * @param {string} username - User's username
   * @param {string} password - User's password
   * @returns {Promise} - Returns user data and access token
   */
  /**
   * Decode JWT token to get user info and roles
   * @param {string} token - JWT token
   * @returns {object} - Decoded token payload
   */
  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  }

  async login(username, password) {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post(`${AUTH_API_URL}/auth/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.data.access_token) {
        const tokenPayload = this.decodeToken(response.data.access_token);
        const userData = {
          token: response.data.access_token,
          tokenType: response.data.token_type,
          username: username,
          roles: tokenPayload?.roles || [],
          sub: tokenPayload?.sub,
          exp: tokenPayload?.exp,
        };
        localStorage.setItem('user', JSON.stringify(userData));
        return userData;
      }
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Register a new user
   * @param {object} userData - User registration data
   * @returns {Promise} - Returns created user data
   */
  async register(userData) {
    try {
      const response = await axios.post(`${AUTH_API_URL}/auth/register`, userData);
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Register a new admin user (admin-only endpoint)
   * @param {object} userData - Admin user registration data
   * @returns {Promise} - Returns created admin user data
   */
  async registerAdmin(userData) {
    try {
      const response = await axios.post(
        `${AUTH_API_URL}/auth/register-admin`,
        userData,
        {
          headers: this.getAuthHeader(),
        }
      );
      return response.data;
    } catch (error) {
      throw this._handleError(error);
    }
  }

  /**
   * Logout current user
   */
  logout() {
    localStorage.removeItem('user');
  }

  /**
   * Get current user from localStorage
   * @returns {object|null} - Current user object or null
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  }

  /**
   * Get authentication token
   * @returns {string|null} - JWT token or null
   */
  getToken() {
    const user = this.getCurrentUser();
    return user ? user.token : null;
  }

  /**
   * Check if user is authenticated
   * @returns {boolean} - True if authenticated, false otherwise
   */
  isAuthenticated() {
    return !!this.getToken();
  }

  /**
   * Check if current user has admin role
   * @returns {boolean} - True if user is admin
   */
  isAdmin() {
    const user = this.getCurrentUser();
    return user && user.roles && user.roles.includes('admin');
  }

  /**
   * Check if current user has specific role
   * @param {string} role - Role to check
   * @returns {boolean} - True if user has the role
   */
  hasRole(role) {
    const user = this.getCurrentUser();
    return user && user.roles && user.roles.includes(role);
  }

  /**
   * Get authentication headers
   * @returns {object} - Headers with Bearer token
   */
  getAuthHeader() {
    const token = this.getToken();
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }

  /**
   * Handle API errors
   * @private
   */
  _handleError(error) {
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return new Error(message);
    } else if (error.request) {
      // No response received
      return new Error('No response from server. Please check your connection.');
    } else {
      // Request setup error
      return new Error(error.message || 'An error occurred');
    }
  }
}

export default new AuthService();
