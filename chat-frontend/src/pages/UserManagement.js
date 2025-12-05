import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { VERSION } from '../config/version';
import authService from '../services/authService';
import chatService from '../services/chatService';
import './UserManagement.css';

const UserManagement = () => {
  const navigate = useNavigate();
  const { user, logout, isAdmin } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingUser, setDeletingUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await authService.getAllUsers();
      setUsers(response.users || []);
    } catch (err) {
      console.error('Failed to load users:', err);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/chat');
      return;
    }
    loadUsers();
  }, [isAdmin, navigate, loadUsers]);

  const handleDeleteUser = async (username) => {
    // Prevent deleting the default admin
    if (username === 'admin') {
      alert('Cannot delete the default admin user.');
      return;
    }

    // Prevent self-deletion
    if (username === user?.username) {
      alert('You cannot delete your own account.');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete user "${username}"?\n\nThis will permanently remove:\n• User account\n• All conversations and messages\n• All analytics data\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingUser(username);
      
      // Delete from chat-service (includes conversations, messages, MCP servers, and analytics)
      try {
        await chatService.deleteUserAdmin(username);
      } catch (err) {
        // User might not exist in chat database, continue
        console.log('Chat service deletion:', err.message);
      }

      // Delete from auth-service
      await authService.deleteUser(username);

      // Update local state
      setUsers(prev => prev.filter(u => u.username !== username));
      
      alert(`User "${username}" has been successfully deleted from all systems.`);
    } catch (err) {
      console.error('Failed to delete user:', err);
      alert(`Failed to delete user: ${err.message}`);
    } finally {
      setDeletingUser(null);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const filteredUsers = users.filter(u => 
    u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.roles?.some(r => r.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="user-management-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management-page">
      <div className="user-management-header">
        <div className="header-left">
          <button onClick={() => navigate('/chat')} className="back-btn">
            ← Back to Chat
          </button>
          <div className="header-logo">
            <span className="logo-icon">💬</span>
            <span className="logo-text">ConvoAI</span>
            <span className="version-badge">v{VERSION}</span>
          </div>
          <h1>👥 User Management</h1>
        </div>
        <div className="header-right">
          <button onClick={toggleTheme} className="theme-toggle-btn" title={`Switch to ${isDark ? 'light' : 'dark'} mode`}>
            {isDark ? '☀️ Light' : '🌙 Dark'}
          </button>
          <span className="username">👤 {user?.username}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>

      <div className="user-management-content">
        <div className="toolbar">
          <div className="search-container">
            <input
              type="text"
              placeholder="Search users by name, email, or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button onClick={() => setSearchTerm('')} className="clear-search">
                ✕
              </button>
            )}
          </div>
          <div className="toolbar-actions">
            <button onClick={loadUsers} className="refresh-btn" disabled={loading}>
              🔄 Refresh
            </button>
            <button onClick={() => navigate('/register-admin')} className="create-admin-btn">
              ➕ Create Admin
            </button>
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
            <button onClick={loadUsers}>Try Again</button>
          </div>
        )}

        <div className="users-summary">
          Showing {filteredUsers.length} of {users.length} users
        </div>

        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Roles</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan="5" className="no-users">
                    {searchTerm ? 'No users match your search.' : 'No users found.'}
                  </td>
                </tr>
              ) : (
                filteredUsers.map((userData) => (
                  <tr key={userData.id || userData.username}>
                    <td>
                      <strong>{userData.username}</strong>
                      {userData.username === 'admin' && (
                        <span className="default-admin-badge">Default Admin</span>
                      )}
                      {userData.username === user?.username && (
                        <span className="current-user-badge">You</span>
                      )}
                    </td>
                    <td>{userData.email || 'N/A'}</td>
                    <td>
                      <div className="roles-list">
                        {userData.roles?.map((role, idx) => (
                          <span key={idx} className={`role-badge ${role}`}>
                            {role}
                          </span>
                        )) || 'N/A'}
                      </div>
                    </td>
                    <td>{formatDate(userData.created_at)}</td>
                    <td>
                      <div className="action-buttons">
                        {userData.username !== 'admin' && userData.username !== user?.username ? (
                          <button
                            className="delete-btn"
                            onClick={() => handleDeleteUser(userData.username)}
                            disabled={deletingUser === userData.username}
                          >
                            {deletingUser === userData.username ? (
                              <>
                                <span className="btn-spinner"></span>
                                Deleting...
                              </>
                            ) : (
                              '🗑️ Delete'
                            )}
                          </button>
                        ) : (
                          <span className="protected-user">
                            {userData.username === 'admin' ? '🔒 Protected' : '👤 Current User'}
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="user-management-footer">
          <p className="info-text">
            ⚠️ Deleting a user will permanently remove their account, all conversations, messages, and analytics data.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
