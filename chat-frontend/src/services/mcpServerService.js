import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_CHAT_API_URL || 'http://localhost:8000';

class MCPServerService {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach auth token
    this.api.interceptors.request.use(
      (config) => {
        // Get token from user object in localStorage (same as authService)
        const userStr = localStorage.getItem('user');
        if (userStr) {
          try {
            const user = JSON.parse(userStr);
            if (user.token) {
              config.headers.Authorization = `Bearer ${user.token}`;
            }
          } catch (e) {
            console.error('Failed to parse user from localStorage:', e);
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  /**
   * Create a new MCP server
   */
  async createMCPServer(mcpServerData) {
    try {
      const response = await this.api.post('/mcp-servers/', mcpServerData);
      return response.data;
    } catch (error) {
      console.error('Failed to create MCP server:', error);
      throw error;
    }
  }

  /**
   * Get all MCP servers for current user
   */
  async getMCPServers(activeOnly = false) {
    try {
      console.log('[MCPServerService] Fetching MCP servers, activeOnly:', activeOnly);
      const response = await this.api.get('/mcp-servers/', {
        params: { active_only: activeOnly },
      });
      console.log('[MCPServerService] Response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[MCPServerService] Failed to fetch MCP servers:', error);
      if (error.response) {
        console.error('[MCPServerService] Response status:', error.response.status);
        console.error('[MCPServerService] Response data:', error.response.data);
      }
      throw error;
    }
  }

  /**
   * Get a specific MCP server by ID
   */
  async getMCPServer(serverId) {
    try {
      const response = await this.api.get(`/mcp-servers/${serverId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch MCP server:', error);
      throw error;
    }
  }

  /**
   * Update an MCP server
   */
  async updateMCPServer(serverId, updateData) {
    try {
      const response = await this.api.put(`/mcp-servers/${serverId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Failed to update MCP server:', error);
      throw error;
    }
  }

  /**
   * Delete an MCP server
   */
  async deleteMCPServer(serverId) {
    try {
      const response = await this.api.delete(`/mcp-servers/${serverId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to delete MCP server:', error);
      throw error;
    }
  }

  /**
   * Get all MCP servers (Admin only)
   */
  async getAllMCPServers(activeOnly = false) {
    try {
      const response = await this.api.get('/admin/mcp-servers/', {
        params: { active_only: activeOnly },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch all MCP servers:', error);
      throw error;
    }
  }
}

const mcpServerService = new MCPServerService();
export default mcpServerService;
