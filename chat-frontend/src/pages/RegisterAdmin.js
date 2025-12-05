import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { VERSION } from '../config/version';
import authService from '../services/authService';
import './RegisterAdmin.css';

const RegisterAdmin = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, logout, isAdmin } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const navigate = useNavigate();

  // Redirect if not admin
  React.useEffect(() => {
    if (!isAdmin()) {
      navigate('/chat');
    }
  }, [isAdmin, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear messages when user types
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      };

      const result = await authService.registerAdmin(userData);
      setSuccess(result.message || 'Admin account created successfully!');
      
      // Clear form
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
      });

      // Show success message for 3 seconds, then redirect
      setTimeout(() => {
        navigate('/chat');
      }, 3000);
    } catch (err) {
      setError(err.message || 'Failed to create admin account');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/chat');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAdmin()) {
    return null;
  }

  return (
    <div className="register-container">
      <div className="page-header">
        <div className="header-left">
          <button onClick={handleCancel} className="back-button">
            ← Back to Chat
          </button>
          <div className="header-logo">
            <span className="logo-icon">💬</span>
            <span className="logo-text">ConvoAI</span>
            <span className="version-badge">v{VERSION}</span>
          </div>
        </div>
        <div className="header-right">
          <button onClick={toggleTheme} className="theme-toggle-btn" title={`Switch to ${isDark ? 'light' : 'dark'} mode`}>
            {isDark ? '☀️ Light' : '🌙 Dark'}
          </button>
          <span className="username">👤 {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
      <div className="register-card">
        <h1 className="register-title">👤 Admin Panel</h1>
        <h2 className="register-subtitle">Create Admin Account</h2>
        
        {error && <div className="error-message">❌ {error}</div>}
        {success && <div className="success-message">✅ {success}</div>}
        
        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              disabled={loading}
              autoComplete="off"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter email address"
              required
              disabled={loading}
              autoComplete="off"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="full_name">Full Name</label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter full name"
              disabled={loading}
              autoComplete="off"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password (min 6 characters)"
              required
              disabled={loading}
              autoComplete="new-password"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password *</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm the password"
              required
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <div className="admin-info">
            <strong>Note:</strong> This will create an account with admin privileges.
            The user will have access to analytics and administrative features.
          </div>
          
          <div className="button-group">
            <button type="submit" className="register-button" disabled={loading}>
              {loading ? 'Creating admin account...' : '🔐 Create Admin Account'}
            </button>
            <button 
              type="button" 
              className="cancel-button" 
              onClick={handleCancel}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterAdmin;
