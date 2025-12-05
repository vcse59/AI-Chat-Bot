import React, { useState, useEffect } from 'react';
import mcpServerService from '../services/mcpServerService';
import './MCPServerManager.css';

// Default MCP Server configuration
const DEFAULT_MCP_SERVER = {
  name: 'Timezone MCP Server',
  description: 'Built-in MCP server for timezone conversions, current time queries, and date/time calculations. Useful for scheduling and time-related queries.',
  server_url: 'http://localhost:8003',
  is_active: true,
  isDefault: true,
};

const MCPServerManager = () => {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
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

  // Add default server to display if not already in list
  const hasDefaultServer = servers.some(s => s.name === DEFAULT_MCP_SERVER.name);
  const displayServers = hasDefaultServer ? servers : [{ ...DEFAULT_MCP_SERVER, id: 'default' }, ...servers];

  // Function to add default server
  const handleAddDefaultServer = async () => {
    try {
      const { isDefault, ...serverData } = DEFAULT_MCP_SERVER;
      await mcpServerService.createMCPServer(serverData);
      await loadServers();
    } catch (err) {
      setError('Failed to add default server');
      console.error(err);
    }
  };

  return (
    <div className="mcp-server-manager">
      <div className="mcp-header">
        <h2>🔌 MCP Server Management</h2>
        <div className="header-actions">
          <button 
            className="btn btn-info"
            onClick={() => setShowInstructions(!showInstructions)}
          >
            {showInstructions ? 'Hide Instructions' : '📖 How to Add MCP Server'}
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            {showAddForm ? 'Cancel' : '+ Add MCP Server'}
          </button>
        </div>
      </div>

      {/* Instructions Section */}
      {showInstructions && (
        <div className="mcp-instructions">
          <h3>📚 How to Add and Configure MCP Servers</h3>
          <div className="instructions-content">
            <div className="instruction-step">
              <span className="step-number">1</span>
              <div className="step-content">
                <h4>What is MCP?</h4>
                <p>Model Context Protocol (MCP) servers extend the AI's capabilities by providing additional tools and context. They allow the chat to access external services, databases, and APIs.</p>
              </div>
            </div>
            
            <div className="instruction-step">
              <span className="step-number">2</span>
              <div className="step-content">
                <h4>Adding a New Server</h4>
                <p>Click the <strong>"+ Add MCP Server"</strong> button and fill in:</p>
                <ul>
                  <li><strong>Server Name:</strong> A friendly name for the server</li>
                  <li><strong>Description:</strong> What capabilities the server provides</li>
                  <li><strong>Server URL:</strong> The HTTP endpoint (e.g., http://localhost:8003)</li>
                  <li><strong>Active:</strong> Enable/disable the server</li>
                </ul>
              </div>
            </div>
            
            <div className="instruction-step">
              <span className="step-number">3</span>
              <div className="step-content">
                <h4>Default Server</h4>
                <p>The <strong>Timezone MCP Server</strong> is included by default. It provides timezone conversions, current time queries, and date calculations. Click "Add to My Servers" to enable it.</p>
              </div>
            </div>
            
            <div className="instruction-step">
              <span className="step-number">4</span>
              <div className="step-content">
                <h4>Creating Custom MCP Servers</h4>
                <p>You can create your own MCP servers following the protocol specification. See the <code>timezone-mcp-server</code> folder in the project for an example implementation.</p>
              </div>
            </div>
          </div>
        </div>
      )}

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
        <h3 className="section-title">📡 Available MCP Servers</h3>
        
        {/* Default Server Card - Always shown if not added */}
        {!hasDefaultServer && (
          <div className="default-server-section">
            <div className="server-card default-server">
              <div className="default-badge">⭐ Recommended</div>
              <div className="server-header">
                <h3>🌍 {DEFAULT_MCP_SERVER.name}</h3>
                <div className="server-status">
                  <span className="status-badge pending">Not Added</span>
                </div>
              </div>
              
              <p className="server-description">{DEFAULT_MCP_SERVER.description}</p>
              
              <div className="server-details">
                <div className="detail-item">
                  <span className="detail-label">URL:</span>
                  <span className="detail-value">{DEFAULT_MCP_SERVER.server_url}</span>
                </div>
              </div>
              
              <div className="server-actions">
                <button 
                  className="btn btn-success"
                  onClick={handleAddDefaultServer}
                >
                  ✓ Add to My Servers
                </button>
              </div>
            </div>
          </div>
        )}

        {servers.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔌</div>
            <p>No custom MCP servers configured yet.</p>
            <p>Add the default Timezone server above or click "+ Add MCP Server" to add your own.</p>
          </div>
        ) : (
          <div className="servers-grid">
            {servers.map((server) => (
              <div key={server.id} className={`server-card ${!server.is_active ? 'inactive' : ''} ${server.name === DEFAULT_MCP_SERVER.name ? 'is-default' : ''}`}>
                {server.name === DEFAULT_MCP_SERVER.name && (
                  <div className="default-badge">⭐ Default</div>
                )}
                <div className="server-header">
                  <h3>{server.name === DEFAULT_MCP_SERVER.name ? '🌍 ' : ''}{server.name}</h3>
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
