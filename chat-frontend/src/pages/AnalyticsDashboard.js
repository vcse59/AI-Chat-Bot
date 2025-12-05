import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { VERSION } from '../config/version';
import analyticsService from '../services/analyticsService';
import chatService from '../services/chatService';
import authService from '../services/authService';
import MetricsCard from '../components/MetricsCard';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [initialLoading, setInitialLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [activities, setActivities] = useState([]);
  const [topUsers, setTopUsers] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [activeTab, setActiveTab] = useState('overview'); // overview, roles, users, conversations, admin-conversations, tokens, response-times
  
  // Enhanced metrics state
  const [metricsByRole, setMetricsByRole] = useState([]);
  const [userMetrics, setUserMetrics] = useState([]);
  const [allConversations, setAllConversations] = useState([]);
  const [adminConversations, setAdminConversations] = useState([]);
  const [deletingConvId, setDeletingConvId] = useState(null);
  const [deletingUserId, setDeletingUserId] = useState(null);
  const [tokenUsage, setTokenUsage] = useState([]);
  const [responseTimes, setResponseTimes] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userConversations, setUserConversations] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    startDate: null,
    endDate: null,
    selectedUserId: null,
    selectedRole: null,
    minTokens: null,
    maxTokens: null,
    sortBy: 'created_at',
    sortOrder: 'desc'
  });
  const [showFilters, setShowFilters] = useState(false);

  // Debounce function to prevent too many rapid refreshes
  const debounceTimeout = React.useRef(null);

  const debouncedRefresh = useCallback(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }
    debounceTimeout.current = setTimeout(() => {
      // Refresh all data to keep tabs in sync
      loadDashboardData(false);
      loadEnhancedMetrics();
    }, 500); // Wait 500ms before refreshing
  }, []);

  useEffect(() => {
    loadDashboardData(true);
    loadEnhancedMetrics(true); // Load all data initially with loading state
    
    // Set up auto-refresh every 3 seconds for real-time updates
    // Refresh ALL data silently to keep everything in sync with DB
    const interval = setInterval(() => {
      loadDashboardData(false); // Silent refresh without loading state
      loadEnhancedMetrics(false); // Silent refresh keeps all tabs fresh
    }, 3000);
    
    // Listen for conversation change events
    const handleConversationChange = (event) => {
      console.log('Analytics: Conversation changed:', event.detail);
      // Immediately refresh all analytics data
      debouncedRefresh();
    };
    
    // Listen for message added events
    const handleMessageAdded = (event) => {
      console.log('Analytics: Message added:', event.detail);
      // Add a small delay to allow backend analytics tracking to complete
      setTimeout(() => {
        debouncedRefresh();
      }, 1000);
    };
    
    window.addEventListener('conversationChanged', handleConversationChange);
    window.addEventListener('messageAdded', handleMessageAdded);
    
    return () => {
      clearInterval(interval);
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      window.removeEventListener('conversationChanged', handleConversationChange);
      window.removeEventListener('messageAdded', handleMessageAdded);
    };
  }, [debouncedRefresh]);

  const loadDashboardData = async (isInitial = false) => {
    try {
      if (isInitial) {
        setInitialLoading(true);
      } else {
        setLoading(true);
      }
      setError(null);

      // Load all analytics data
      const [summaryData, activitiesData, topUsersData] = await Promise.all([
        analyticsService.getSummary(),
        analyticsService.getUserActivities(0, 10),
        analyticsService.getTopUsers(5),
      ]);

      setSummary(summaryData);
      setActivities(activitiesData);
      setTopUsers(topUsersData);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError(err.message || 'Failed to load analytics data');
    } finally {
      if (isInitial) {
        setInitialLoading(false);
      } else {
        setLoading(false);
      }
    }
  };

  const loadEnhancedMetrics = async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const [roleData, analyticsUserData, conversationsData, tokenData, responseData, authUsersData] = await Promise.all([
        analyticsService.getMetricsByRole(),
        analyticsService.getUsersDetailedMetrics(null, 50),
        analyticsService.getConversationMetrics({ limit: 100 }),
        analyticsService.getTokenUsageByConversation(null, 50),
        analyticsService.getResponseTimesByUser(50),
        authService.getAllUsers().catch(() => ({ users: [] })), // Fallback if auth service fails
      ]);

      // Merge auth users with analytics data
      // Create a map of analytics users by username for quick lookup
      const analyticsUserMap = new Map();
      analyticsUserData.forEach(user => {
        analyticsUserMap.set(user.username, user);
      });

      // Create merged user list - include all auth users with analytics data where available
      const authUsers = authUsersData.users || [];
      const mergedUsers = authUsers.map(authUser => {
        const analyticsData = analyticsUserMap.get(authUser.username);
        if (analyticsData) {
          // User has analytics data, use it but ensure username matches
          return { ...analyticsData, role: authUser.roles?.[0] || analyticsData.role };
        } else {
          // User has no analytics data, create placeholder
          return {
            user_id: authUser.id || authUser.username,
            username: authUser.username,
            role: authUser.roles?.[0] || 'user',
            total_conversations: 0,
            total_messages: 0,
            total_tokens: 0,
            avg_response_time: 0,
          };
        }
      });

      // Also include any analytics users not in auth (shouldn't happen normally)
      analyticsUserData.forEach(analyticsUser => {
        if (!authUsers.find(au => au.username === analyticsUser.username)) {
          mergedUsers.push(analyticsUser);
        }
      });

      setMetricsByRole(roleData);
      setUserMetrics(mergedUsers);
      setAllConversations(conversationsData);
      setTokenUsage(tokenData);
      setResponseTimes(responseData);
    } catch (err) {
      console.error('Failed to load enhanced metrics:', err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const loadAdminConversations = async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const conversations = await chatService.getAllConversationsAdmin();
      setAdminConversations(conversations);
    } catch (err) {
      console.error('Failed to load admin conversations:', err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const loadUserConversations = async (userId) => {
    try {
      const conversations = await analyticsService.getUserConversations(userId, 50);
      setUserConversations(conversations);
      setSelectedUser(userId);
    } catch (err) {
      console.error('Failed to load user conversations:', err);
    }
  };

  useEffect(() => {
    if (activeTab !== 'overview') {
      // Only load if we don't have data yet
      const needsLoad = 
        (activeTab === 'roles' && metricsByRole.length === 0) ||
        (activeTab === 'users' && userMetrics.length === 0) ||
        (activeTab === 'conversations' && allConversations.length === 0) ||
        (activeTab === 'tokens' && tokenUsage.length === 0) ||
        (activeTab === 'response-times' && responseTimes.length === 0);
      
      if (needsLoad) {
        loadEnhancedMetrics();
      }
    }
    if (activeTab === 'admin-conversations') {
      loadAdminConversations();
    }
  }, [activeTab]);

  const applyFilters = () => {
    loadEnhancedMetrics();
  };

  const clearFilters = () => {
    setFilters({
      startDate: null,
      endDate: null,
      selectedUserId: null,
      selectedRole: null,
      minTokens: null,
      maxTokens: null,
      sortBy: 'created_at',
      sortOrder: 'desc'
    });
    loadEnhancedMetrics();
  };

  const filteredUserMetrics = useMemo(() => {
    return userMetrics.filter(user => {
      if (filters.selectedRole && user.role !== filters.selectedRole) return false;
      if (filters.minTokens && user.total_tokens < parseInt(filters.minTokens)) return false;
      if (filters.maxTokens && user.total_tokens > parseInt(filters.maxTokens)) return false;
      return true;
    });
  }, [userMetrics, filters.selectedRole, filters.minTokens, filters.maxTokens]);

  const filteredTokenUsage = useMemo(() => {
    return tokenUsage.filter(conv => {
      if (filters.selectedUserId && conv.user_id !== filters.selectedUserId) return false;
      if (filters.minTokens && conv.total_tokens < parseInt(filters.minTokens)) return false;
      if (filters.maxTokens && conv.total_tokens > parseInt(filters.maxTokens)) return false;
      if (filters.startDate && new Date(conv.created_at) < new Date(filters.startDate)) return false;
      if (filters.endDate && new Date(conv.created_at) > new Date(filters.endDate)) return false;
      return true;
    });
  }, [tokenUsage, filters.selectedUserId, filters.minTokens, filters.maxTokens, filters.startDate, filters.endDate]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleClearAllStats = async () => {
    if (!showClearConfirm) {
      setShowClearConfirm(true);
      return;
    }

    try {
      setClearing(true);
      await analyticsService.clearAllStats();
      setShowClearConfirm(false);
      // Reload the dashboard to show empty stats
      await loadDashboardData();
    } catch (err) {
      console.error('Failed to clear analytics:', err);
      setError(err.message || 'Failed to clear analytics data');
    } finally {
      setClearing(false);
    }
  };

  const handleCancelClear = () => {
    setShowClearConfirm(false);
  };

  const handleDeleteConversation = async (conversationId) => {
    if (!window.confirm('Are you sure you want to permanently delete this conversation? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingConvId(conversationId);
      await chatService.deleteConversationAdmin(conversationId);
      
      // Update local state without full page reload
      setAdminConversations(prev => prev.filter(conv => conv.id !== conversationId));
      setAllConversations(prev => prev.filter(conv => conv.conversation_id !== conversationId));
      
      // Update summary counts locally
      setSummary(prev => ({
        ...prev,
        total_conversations: (prev.total_conversations || 0) - 1,
        active_conversations: (prev.active_conversations || 0) - 1
      }));
      
      // Dispatch events for other components to update
      window.dispatchEvent(new CustomEvent('conversationChanged', {
        detail: { action: 'deleted', conversationId }
      }));
      
      // Dispatch special event for chat page to remove from sidebar
      window.dispatchEvent(new CustomEvent('conversationDeleted', {
        detail: { action: 'deleted', conversationId }
      }));
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      alert(`Failed to delete conversation: ${err.message}`);
    } finally {
      setDeletingConvId(null);
    }
  };

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

    if (!window.confirm(`Are you sure you want to permanently delete user "${username}"?\n\nThis will permanently remove:\n• User account from auth system\n• All conversations and messages\n• All analytics data\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingUserId(username);
      
      // Step 1: Delete from chat-service (includes conversations, messages, MCP servers, and analytics)
      try {
        await chatService.deleteUserAdmin(username);
      } catch (err) {
        // User might not exist in chat database, continue with auth deletion
        console.log('Chat service deletion:', err.message);
      }

      // Step 2: Delete from auth-service (the primary user account)
      await authService.deleteUser(username);
      
      // Update local state without full page reload
      setUserMetrics(prev => prev.filter(user => user.username !== username));
      
      // Update summary counts locally
      setSummary(prev => ({
        ...prev,
        total_users: (prev.total_users || 0) - 1
      }));
      
      // Dispatch event for other components to update
      window.dispatchEvent(new CustomEvent('userDeleted', {
        detail: { username }
      }));
      
      alert(`User "${username}" has been successfully deleted from all systems.`);
    } catch (err) {
      console.error('Failed to delete user:', err);
      let errorMessage = err.message;
      
      // Provide more helpful error messages
      if (errorMessage.includes('User not found') || errorMessage.includes('404')) {
        errorMessage = `User "${username}" not found in auth system. The user may have already been deleted.`;
      }
      
      alert(`Failed to delete user: ${errorMessage}`);
    } finally {
      setDeletingUserId(null);
    }
  };

  const handleBackToChat = () => {
    navigate('/chat');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const getActivityIcon = (activityType) => {
    const icons = {
      login: '🔐',
      logout: '🚪',
      api_call: '📡',
      message_sent: '💬',
      conversation_started: '🆕',
      conversation_ended: '✅',
      error: '❌',
    };
    return icons[activityType] || '📊';
  };

  if (initialLoading) {
    return (
      <div className="analytics-dashboard">
        <div className="analytics-header">
          <div className="header-logo">
            <span className="logo-icon">💬</span>
            <span className="logo-text">ConvoAI</span>
            <span className="version-badge">v{VERSION}</span>
          </div>
          <h1>📊 Analytics Dashboard</h1>
          <p>Loading analytics data...</p>
        </div>
        <div className="analytics-loading">
          <div className="analytics-loading-spinner"></div>
          <div className="analytics-loading-text">Loading analytics...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard">
        <div className="analytics-header">
          <div className="header-logo">
            <span className="logo-icon">💬</span>
            <span className="logo-text">ConvoAI</span>
            <span className="version-badge">v{VERSION}</span>
          </div>
          <h1>📊 Analytics Dashboard</h1>
          <p>Admin-only analytics and metrics</p>
        </div>
        <div className="analytics-error">
          <div className="analytics-error-icon">🚫</div>
          <h2>Access Denied</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="page-header">
        <div className="header-left">
          <button onClick={handleBackToChat} className="back-button">
            ← Back to Chat
          </button>
          <div className="header-logo">
            <span className="logo-icon">💬</span>
            <span className="logo-text">ConvoAI</span>
            <span className="version-badge">v{VERSION}</span>
          </div>
          <h1>📊 Analytics Dashboard</h1>
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
      <div className="analytics-header">
        <p>Real-time metrics and user activity insights</p>
      </div>

      {/* Filter Toggle Button */}
      <div className="filter-bar">
        <button 
          className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          🔍 Filters {showFilters ? '▼' : '▶'}
        </button>
        {showFilters && (
          <button className="clear-filters-btn" onClick={clearFilters}>
            ✕ Clear Filters
          </button>
        )}
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filters-grid">
            <div className="filter-group">
              <label>Start Date</label>
              <input
                type="date"
                value={filters.startDate || ''}
                onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>End Date</label>
              <input
                type="date"
                value={filters.endDate || ''}
                onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>User Role</label>
              <select
                value={filters.selectedRole || ''}
                onChange={(e) => setFilters({ ...filters, selectedRole: e.target.value || null })}
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="user">User</option>
              </select>
            </div>
            <div className="filter-group">
              <label>User</label>
              <select
                value={filters.selectedUserId || ''}
                onChange={(e) => setFilters({ ...filters, selectedUserId: e.target.value || null })}
              >
                <option value="">All Users</option>
                {userMetrics.map((user, idx) => (
                  <option key={idx} value={user.user_id}>
                    {user.username}
                  </option>
                ))}
              </select>
            </div>
            <div className="filter-group">
              <label>Min Tokens</label>
              <input
                type="number"
                placeholder="Min"
                value={filters.minTokens || ''}
                onChange={(e) => setFilters({ ...filters, minTokens: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>Max Tokens</label>
              <input
                type="number"
                placeholder="Max"
                value={filters.maxTokens || ''}
                onChange={(e) => setFilters({ ...filters, maxTokens: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              >
                <option value="created_at">Date</option>
                <option value="total_tokens">Tokens</option>
                <option value="message_count">Messages</option>
                <option value="username">Username</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Sort Order</label>
              <select
                value={filters.sortOrder}
                onChange={(e) => setFilters({ ...filters, sortOrder: e.target.value })}
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>
          <div className="filter-actions">
            <button className="apply-filters-btn" onClick={applyFilters}>
              Apply Filters
            </button>
            <button className="clear-filters-btn" onClick={clearFilters}>
              Clear All
            </button>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="analytics-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          👥 By Role
        </button>
        <button 
          className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          👤 By User
        </button>
        <button 
          className={`tab-button ${activeTab === 'conversations' ? 'active' : ''}`}
          onClick={() => setActiveTab('conversations')}
        >
          💬 Conversations
        </button>
        <button 
          className={`tab-button ${activeTab === 'admin-conversations' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin-conversations')}
        >
          🔒 All Conversations (Admin)
        </button>
        <button 
          className={`tab-button ${activeTab === 'tokens' ? 'active' : ''}`}
          onClick={() => setActiveTab('tokens')}
        >
          🎫 Token Usage
        </button>
        <button 
          className={`tab-button ${activeTab === 'response-times' ? 'active' : ''}`}
          onClick={() => setActiveTab('response-times')}
        >
          ⚡ Response Times
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          {/* Key Metrics */}
          <div className="metrics-grid">
            <MetricsCard
              title="Total Users"
              value={summary?.total_users || 0}
              subtitle="Registered accounts"
              icon="👥"
              iconType="users"
            />
            <MetricsCard
              title="Active Users"
              value={summary?.active_users_today || 0}
              subtitle="Recently active"
              icon="✅"
              iconType="users"
            />
            <MetricsCard
              title="Total Conversations"
              value={summary?.total_conversations || 0}
              subtitle="All time"
              icon="💬"
              iconType="conversations"
            />
            <MetricsCard
              title="Active Conversations"
              value={summary?.active_conversations || 0}
              subtitle="Currently active"
              icon="🔵"
              iconType="active"
            />
            <MetricsCard
              title="Total Messages"
              value={summary?.total_messages || 0}
              subtitle="Messages exchanged"
              icon="📨"
              iconType="messages"
            />
            <MetricsCard
              title="Total Tokens"
              value={summary?.total_tokens || 0}
              subtitle="API usage"
              icon="🎫"
              iconType="tokens"
            />
            <MetricsCard
              title="Avg Response Time"
              value={
                summary?.avg_response_time
                  ? `${summary.avg_response_time.toFixed(2)}s`
                  : 'N/A'
              }
              subtitle="System performance"
              icon="⚡"
              iconType="response-time"
            />
          </div>

          {/* Recent Activities */}
          <div className="analytics-section">
            <div className="analytics-section-header">
              <h2>Recent User Activity</h2>
              <div className="analytics-actions">
                <button
                  className="refresh-button"
                  onClick={handleRefresh}
                  disabled={refreshing}
                >
                  {refreshing ? '🔄 Refreshing...' : '🔄 Refresh'}
                </button>
                {!showClearConfirm ? (
                  <button
                    className="clear-stats-button"
                    onClick={handleClearAllStats}
                    disabled={clearing}
                    title="Clear all analytics data"
                  >
                    🗑️ Clear All Stats
                  </button>
                ) : (
                  <div className="clear-confirm-buttons">
                    <button
                      className="clear-confirm-yes"
                      onClick={handleClearAllStats}
                      disabled={clearing}
                    >
                      {clearing ? '⏳ Clearing...' : '✓ Yes, Clear All'}
                    </button>
                    <button
                      className="clear-confirm-no"
                      onClick={handleCancelClear}
                      disabled={clearing}
                    >
                      ✗ Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
            <div className="activity-list">
              {activities && activities.length > 0 ? (
                activities.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">
                      {getActivityIcon(activity.activity_type)}
                    </div>
                    <div className="activity-details">
                      <div className="activity-username">
                        {activity.username || activity.user_id}
                      </div>
                      <div>
                        <span className="activity-type">{activity.activity_type}</span>
                        <span className="activity-timestamp">
                          {formatTimestamp(activity.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">📭</div>
                  <div className="empty-state-text">No recent activity</div>
                </div>
              )}
            </div>
          </div>

          {/* Top Users */}
          <div className="analytics-section">
            <div className="analytics-section-header">
              <h2>Most Active Users</h2>
            </div>
            <div className="top-users-list">
              {topUsers && topUsers.length > 0 ? (
                topUsers.map((user, index) => (
                  <div key={index} className="top-user-item">
                    <div className="top-user-rank">#{index + 1}</div>
                    <div className="top-user-details">
                      <div className="top-user-username">
                        {user.username || user.user_id}
                      </div>
                      <div className="top-user-stats">
                        {user.activity_count} activities
                      </div>
                    </div>
                    <div className="top-user-count">{user.activity_count}</div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">👤</div>
                  <div className="empty-state-text">No user data available</div>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Metrics by Role Tab */}
      {activeTab === 'roles' && (
        <div className="analytics-section">
          <h2>Metrics by User Role</h2>
          <div className="metrics-table">
            <table>
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Users</th>
                  <th>Conversations</th>
                  <th>Messages</th>
                  <th>Tokens</th>
                  <th>Avg Response Time</th>
                </tr>
              </thead>
              <tbody>
                {metricsByRole.map((roleData, index) => (
                  <tr key={index}>
                    <td><strong>{roleData.role}</strong></td>
                    <td>{roleData.user_count}</td>
                    <td>{roleData.total_conversations}</td>
                    <td>{roleData.total_messages}</td>
                    <td>{roleData.total_tokens}</td>
                    <td>{roleData.avg_response_time.toFixed(4)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Conversations Tab */}
      {activeTab === 'conversations' && (
        <div className="analytics-section">
          <h2>All Conversations</h2>
          <div className="results-summary">
            Showing {allConversations.length} conversations
          </div>
          <div className="metrics-table">
                <table>
                  <thead>
                    <tr>
                      <th>Conversation ID</th>
                      <th>User</th>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Messages</th>
                      <th>Tokens</th>
                      <th>Avg Response</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allConversations.length > 0 ? (
                      allConversations.map((conv, index) => (
                        <tr key={index}>
                          <td>{conv.conversation_id?.substring(0, 8)}...</td>
                          <td>{conv.username || conv.user_id || 'N/A'}</td>
                          <td>{conv.title || 'Untitled'}</td>
                          <td>
                            <span className={`status-badge status-${conv.status || 'active'}`}>
                              {conv.status || 'active'}
                            </span>
                          </td>
                          <td>{conv.message_count || 0}</td>
                          <td>{conv.total_tokens || 0}</td>
                          <td>
                            {conv.avg_response_time 
                              ? `${conv.avg_response_time.toFixed(4)}s` 
                              : 'N/A'}
                          </td>
                          <td>{conv.created_at ? new Date(conv.created_at).toLocaleDateString() : 'N/A'}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="8" className="empty-cell">
                          <div className="empty-state">
                            <div className="empty-state-icon">💬</div>
                            <div className="empty-state-text">No conversations found</div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
        </div>
      )}

      {/* Admin Conversations Tab - View and Delete All Conversations */}
      {activeTab === 'admin-conversations' && (
        <div className="analytics-section">
          <h2>🔒 All User Conversations (Admin Only)</h2>
          <div className="results-summary">
            Showing {adminConversations.length} conversations from all users
            <span className="admin-badge">Admin View</span>
              </div>
              <div className="metrics-table">
                <table>
                  <thead>
                    <tr>
                      <th>Conversation ID</th>
                      <th>User</th>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Messages</th>
                      <th>Created</th>
                      <th>Last Updated</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {adminConversations.length > 0 ? (
                      adminConversations.map((conv, index) => (
                        <tr key={index}>
                          <td>
                            <code className="conv-id">{conv.id?.substring(0, 12)}</code>
                          </td>
                          <td>
                            <strong>{conv.user_id || 'Unknown'}</strong>
                          </td>
                          <td>{conv.title || 'Untitled'}</td>
                          <td>
                            <span className={`status-badge status-${conv.status || 'active'}`}>
                              {conv.status || 'active'}
                            </span>
                          </td>
                          <td>{conv.messages?.length || 0}</td>
                          <td>{conv.created_at ? new Date(conv.created_at).toLocaleString() : 'N/A'}</td>
                          <td>{conv.updated_at ? new Date(conv.updated_at).toLocaleString() : 'N/A'}</td>
                          <td>
                            <button
                              className="delete-btn-admin"
                              onClick={() => handleDeleteConversation(conv.id)}
                              disabled={deletingConvId === conv.id}
                              title="Permanently delete this conversation"
                            >
                              {deletingConvId === conv.id ? '⏳' : '🗑️ Delete'}
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="8" className="empty-cell">
                          <div className="empty-state">
                            <div className="empty-state-icon">💬</div>
                            <div className="empty-state-text">No conversations found</div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
        </div>
      )}

      {/* User Metrics Tab */}
      {activeTab === 'users' && (
        <div className="analytics-section">
          <h2>Detailed User Metrics</h2>
          <div className="results-summary">
            Showing {filteredUserMetrics.length} of {userMetrics.length} users
          </div>
          <div className="metrics-table">
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Conversations</th>
                  <th>Messages</th>
                  <th>Tokens</th>
                  <th>Avg Response</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUserMetrics.map((userData) => (
                  <tr key={userData.user_id}>
                    <td><strong>{userData.username}</strong></td>
                    <td>{userData.role || 'N/A'}</td>
                    <td>{userData.total_conversations}</td>
                    <td>{userData.total_messages}</td>
                    <td>{userData.total_tokens}</td>
                    <td>{userData.avg_response_time.toFixed(4)}s</td>
                    <td>
                      <button 
                        className="view-details-btn"
                        onClick={() => loadUserConversations(userData.user_id)}
                      >
                        View Conversations
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* User Conversations Modal */}
      {selectedUser && (
        <div className="modal-overlay" onClick={() => setSelectedUser(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>User Conversations</h3>
            <button className="modal-close" onClick={() => setSelectedUser(null)}>✕</button>
            {userConversations.length > 0 ? (
              <div className="conversations-table">
                <table>
                  <thead>
                    <tr>
                      <th>Conversation ID</th>
                      <th>Messages</th>
                      <th>Tokens</th>
                      <th>Avg Response</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userConversations.map((conv) => (
                      <tr key={conv.conversation_id}>
                        <td>{conv.conversation_id.substring(0, 8)}...</td>
                        <td>{conv.message_count}</td>
                        <td>{conv.total_tokens}</td>
                        <td>{conv.avg_response_time.toFixed(4)}s</td>
                        <td>{new Date(conv.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">💬</div>
                <div className="empty-state-text">No conversations found for this user</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Token Usage Tab */}
      {activeTab === 'tokens' && (
        <div className="analytics-section">
          <h2>Token Usage by Conversation</h2>
          <div className="results-summary">
            Showing {filteredTokenUsage.length} of {tokenUsage.length} conversations
            {filters.minTokens || filters.maxTokens ? (
              <span className="filter-info">
                {' '}(Filtered by tokens: {filters.minTokens || '0'} - {filters.maxTokens || '∞'})
              </span>
            ) : null}
          </div>
          <div className="metrics-table">
                <table>
                  <thead>
                    <tr>
                      <th>Conversation ID</th>
                      <th>Username</th>
                      <th>Total Tokens</th>
                      <th>Messages</th>
                      <th>Avg Tokens/Message</th>
                      <th>Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTokenUsage.map((item, index) => (
                      <tr key={index}>
                        <td>{item.conversation_id.substring(0, 8)}...</td>
                        <td>{item.username || item.user_id}</td>
                        <td><strong>{item.total_tokens}</strong></td>
                        <td>{item.message_count}</td>
                        <td>{item.avg_tokens_per_message}</td>
                        <td>{new Date(item.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        </div>
      )}

      {/* Response Times Tab */}
      {activeTab === 'response-times' && (
        <div className="analytics-section">
          <h2>Response Times by User</h2>
          <div className="metrics-table">
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Messages</th>
                  <th>Avg Response Time</th>
                  <th>Min Response Time</th>
                  <th>Max Response Time</th>
                </tr>
              </thead>
              <tbody>
                {responseTimes.map((item, index) => (
                  <tr key={index}>
                    <td><strong>{item.username || item.user_id}</strong></td>
                    <td>{item.message_count}</td>
                    <td>{item.avg_response_time.toFixed(4)}s</td>
                    <td>{item.min_response_time.toFixed(4)}s</td>
                    <td>{item.max_response_time.toFixed(4)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
