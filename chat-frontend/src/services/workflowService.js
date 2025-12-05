import axios from 'axios';
import authService from './authService';

const LANGCHAIN_API_URL = process.env.REACT_APP_LANGCHAIN_API_URL || 'http://localhost:8004';

class WorkflowService {
  _getAxiosInstance() {
    return axios.create({
      baseURL: LANGCHAIN_API_URL,
      headers: authService.getAuthHeader(),
    });
  }

  async createWorkflow(config) {
    try {
      const api = this._getAxiosInstance();
      // POST to langchain-service endpoint (adjust path as needed)
      const response = await api.post('/api/v1/workflows', config);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
}

const workflowService = new WorkflowService();

export default workflowService;
