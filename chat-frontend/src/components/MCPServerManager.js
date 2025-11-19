import React, { useState, useEffect } from 'react';
import mcpServerService from '../services/mcpServerService';
import './MCPServerManager.css';

const MCPServerManager = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingServer, setEditingServer] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    server_url: '',
    is_active: true,
  });

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      setLoading(true);
      console.log('[MCPServerManager] Loading MCP servers...');
      const data = await mcpServerService.getMCPServers();
      console.log('[MCPServerManager] Loaded servers:', data);
      setServers(data);
      setError(null);
    } catch (err) {
      console.error('[MCPServerManager] Error loading servers:', err);
      
      // Check if it's an authentication error
      if (err.response && err.response.status === 401) {
        setError('Authentication required. Please log in again.');
      } else if (err.response && err.response.status === 404) {
        setError('MCP servers endpoint not found. Please check backend configuration.');
      } else {
        setError(`Failed to load MCP servers: ${err.message || 'Unknown error'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingServer) {
        await mcpServerService.updateMCPServer(editingServer.id, formData);
      } else {
        await mcpServerService.createMCPServer(formData);
      }
      
      // Reset form and reload servers
      resetForm();
      await loadServers();
    } catch (err) {
      setError(editingServer ? 'Failed to update MCP server' : 'Failed to create MCP server');
      console.error(err);
    }
  };

  const handleEdit = (server) => {
    setEditingServer(server);
    setFormData({
      name: server.name,
      description: server.description || '',
      server_url: server.server_url,
      is_active: server.is_active,
    });
    setShowAddForm(true);
  };

  const handleDelete = async (serverId) => {
    if (!window.confirm('Are you sure you want to delete this MCP server?')) {
      return;
    }
    
    try {
      await mcpServerService.deleteMCPServer(serverId);
      await loadServers();
    } catch (err) {
      setError('Failed to delete MCP server');
      console.error(err);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      server_url: '',
      is_active: true,
    });
    setEditingServer(null);
    setShowAddForm(false);
  };

  if (loading && servers.length === 0) {
    return <div className="mcp-server-manager loading">Loading MCP servers...</div>;
  }

  return (
    <div className="mcp-server-manager">
      <div className="mcp-header">
        <h2>MCP Server Management</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : '+ Add MCP Server'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {showAddForm && (
        <div className="mcp-form-container">
          <h3>{editingServer ? 'Edit MCP Server' : 'Add New MCP Server'}</h3>
          <form onSubmit={handleSubmit} className="mcp-form">
            <div className="form-group">
              <label htmlFor="name">Server Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="My MCP Server"
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Brief description of this MCP server"
                rows="3"
              />
            </div>

            <div className="form-group">
              <label htmlFor="server_url">Server URL *</label>
              <input
                type="url"
                id="server_url"
                name="server_url"
                value={formData.server_url}
                onChange={handleInputChange}
                required
                placeholder="http://localhost:8003"
              />
            </div>



            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                />
                <span>Active</span>
              </label>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                {editingServer ? 'Update Server' : 'Create Server'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={resetForm}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="mcp-servers-list">
        {servers.length === 0 ? (
          <div className="empty-state">
            <p>No MCP servers configured yet.</p>
            <p>Click "Add MCP Server" to get started.</p>
          </div>
        ) : (
          <div className="servers-grid">
            {servers.map((server) => (
              <div key={server.id} className={`server-card ${!server.is_active ? 'inactive' : ''}`}>
                <div className="server-header">
                  <h3>{server.name}</h3>
                  <div className="server-status">
                    <span className={`status-badge ${server.is_active ? 'active' : 'inactive'}`}>
                      {server.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                
                {server.description && (
                  <p className="server-description">{server.description}</p>
                )}
                
                <div className="server-details">
                  <div className="detail-item">
                    <span className="detail-label">URL:</span>
                    <span className="detail-value">{server.server_url}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Created:</span>
                    <span className="detail-value">
                      {new Date(server.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                
                <div className="server-actions">
                  <button 
                    className="btn btn-sm btn-secondary"
                    onClick={() => handleEdit(server)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDelete(server.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MCPServerManager;
