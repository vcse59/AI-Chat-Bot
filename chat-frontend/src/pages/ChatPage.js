import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ConversationList from '../components/ConversationList';
import ChatWindow from '../components/ChatWindow';
import analyticsService from '../services/analyticsService';
import MetricsCard from '../components/MetricsCard';
import './ChatPage.css';

const ChatPage = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleToggleAnalytics = async () => {
    setShowAnalytics(!showAnalytics);
    if (!showAnalytics && !analyticsData) {
      await loadAnalytics();
    }
  };

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      const [summary, activities, topUsers] = await Promise.all([
        analyticsService.getSummary(),
        analyticsService.getUserActivities(0, 10),
        analyticsService.getTopUsers(5),
      ]);
      setAnalyticsData({ summary, activities, topUsers });
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  useEffect(() => {
    let interval;
    if (showAnalytics) {
      // Auto-refresh analytics every 30 seconds
      interval = setInterval(loadAnalytics, 30000);
      
      // Load analytics immediately when panel opens
      loadAnalytics();
    }
    
    // Listen for conversation and message changes
    const handleConversationChange = (event) => {
      console.log('ChatPage: Conversation changed:', event.detail);
      if (showAnalytics) {
        loadAnalytics();
      }
    };
    
    const handleMessageAdded = (event) => {
      console.log('ChatPage: Message added:', event.detail);
      if (showAnalytics) {
        // Add a small delay to allow backend analytics tracking to complete
        setTimeout(() => {
          loadAnalytics();
        }, 1000);
      }
    };
    
    if (showAnalytics) {
      window.addEventListener('conversationChanged', handleConversationChange);
      window.addEventListener('messageAdded', handleMessageAdded);
    }
    
    return () => {
      if (interval) clearInterval(interval);
      window.removeEventListener('conversationChanged', handleConversationChange);
      window.removeEventListener('messageAdded', handleMessageAdded);
    };
  }, [showAnalytics]);

  const handleNavigateToRegisterAdmin = () => {
    navigate('/register-admin');
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

  const handleConversationDeleted = async () => {
    // Refresh analytics when a conversation is deleted
    if (showAnalytics) {
      await loadAnalytics();
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>Chat Application</h1>
        <div className="user-info">
          {isAdmin() && (
            <>
              <button onClick={handleToggleAnalytics} className={`analytics-button ${showAnalytics ? 'active' : ''}`}>
                📊 Analytics {showAnalytics ? '✓' : ''}
              </button>
              <button onClick={handleNavigateToRegisterAdmin} className="admin-button">
                👤 Create Admin
              </button>
            </>
          )}
          <span className="username">👤 {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
      
      <div className="chat-content">
        <ConversationList
          selectedConversationId={selectedConversationId}
          onSelectConversation={setSelectedConversationId}
          onConversationDeleted={handleConversationDeleted}
        />
        <ChatWindow conversationId={selectedConversationId} />
        
        {/* Analytics Side Panel */}
        {showAnalytics && (
          <div className="analytics-panel">
            <div className="analytics-panel-header">
              <h2>📊 Analytics</h2>
              <div className="analytics-panel-actions">
                <button 
                  onClick={() => navigate('/analytics')} 
                  className="full-analytics-btn"
                  title="Open full analytics dashboard with filters"
                >
                  🔍 Full Dashboard
                </button>
                <button onClick={loadAnalytics} className="refresh-btn" disabled={analyticsLoading}>
                  🔄 {analyticsLoading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
            </div>
            
            {analyticsLoading && !analyticsData ? (
              <div className="analytics-loading">
                <div className="loading-spinner"></div>
                <p>Loading analytics...</p>
              </div>
            ) : analyticsData ? (
              <div className="analytics-content">
                {/* Metrics Grid */}
                <div className="analytics-metrics">
                  <div className="metric-mini">
                    <div className="metric-icon">👥</div>
                    <div className="metric-info">
                      <div className="metric-value">{analyticsData.summary?.total_users || 0}</div>
                      <div className="metric-label">Total Users</div>
                    </div>
                  </div>
                  <div className="metric-mini">
                    <div className="metric-icon">✅</div>
                    <div className="metric-info">
                      <div className="metric-value">{analyticsData.summary?.active_users_today || 0}</div>
                      <div className="metric-label">Active Today</div>
                    </div>
                  </div>
                  <div className="metric-mini">
                    <div className="metric-icon">💬</div>
                    <div className="metric-info">
                      <div className="metric-value">{analyticsData.summary?.total_conversations || 0}</div>
                      <div className="metric-label">Conversations</div>
                    </div>
                  </div>
                  <div className="metric-mini">
                    <div className="metric-icon">📨</div>
                    <div className="metric-info">
                      <div className="metric-value">{analyticsData.summary?.total_messages || 0}</div>
                      <div className="metric-label">Messages</div>
                    </div>
                  </div>
                  <div className="metric-mini">
                    <div className="metric-icon">🎫</div>
                    <div className="metric-info">
                      <div className="metric-value">{analyticsData.summary?.total_tokens || 0}</div>
                      <div className="metric-label">Tokens</div>
                    </div>
                  </div>
                  <div className="metric-mini">
                    <div className="metric-icon">⚡</div>
                    <div className="metric-info">
                      <div className="metric-value">
                        {analyticsData.summary?.avg_response_time
                          ? `${analyticsData.summary.avg_response_time.toFixed(2)}s`
                          : 'N/A'}
                      </div>
                      <div className="metric-label">Avg Response</div>
                    </div>
                  </div>
                </div>

                {/* Recent Activities */}
                <div className="analytics-section">
                  <h3>Recent Activity</h3>
                  <div className="activity-list-compact">
                    {analyticsData.activities && analyticsData.activities.length > 0 ? (
                      analyticsData.activities.map((activity, index) => (
                        <div key={index} className="activity-item-compact">
                          <span className="activity-icon-small">{getActivityIcon(activity.activity_type)}</span>
                          <div className="activity-details-compact">
                            <div className="activity-user">{activity.username || activity.user_id}</div>
                            <div className="activity-meta">
                              <span className="activity-type-small">{activity.activity_type}</span>
                              <span className="activity-time-small">{formatTimestamp(activity.timestamp)}</span>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="empty-state-compact">No recent activity</div>
                    )}
                  </div>
                </div>

                {/* Top Users */}
                <div className="analytics-section">
                  <h3>Most Active Users</h3>
                  <div className="top-users-compact">
                    {analyticsData.topUsers && analyticsData.topUsers.length > 0 ? (
                      analyticsData.topUsers.map((user, index) => (
                        <div key={index} className="top-user-compact">
                          <span className="user-rank">#{index + 1}</span>
                          <span className="user-name">{user.username || user.user_id}</span>
                          <span className="user-count">{user.activity_count}</span>
                        </div>
                      ))
                    ) : (
                      <div className="empty-state-compact">No user data</div>
                    )}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;
