import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import analyticsService from '../services/analyticsService';
import MetricsCard from '../components/MetricsCard';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [activities, setActivities] = useState([]);
  const [topUsers, setTopUsers] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
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
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
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

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="analytics-header">
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
          <h1>📊 Analytics Dashboard</h1>
        </div>
        <div className="header-right">
          <span className="username">👤 {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
      <div className="analytics-header">
        <p>Real-time metrics and user activity insights</p>
      </div>

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
          value={summary?.active_users || 0}
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
          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? '🔄 Refreshing...' : '🔄 Refresh'}
          </button>
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
    </div>
  );
};

export default AnalyticsDashboard;
