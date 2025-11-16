import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }

  if (!isAdmin()) {
    // Redirect to chat if authenticated but not admin
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f5f7fa',
        padding: '24px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>🚫</div>
        <h1 style={{ color: '#d32f2f', marginBottom: '12px' }}>Access Denied</h1>
        <p style={{ color: '#666', marginBottom: '24px' }}>
          This page is restricted to administrators only.
        </p>
        <button
          onClick={() => window.location.href = '/chat'}
          style={{
            padding: '12px 24px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Go to Chat
        </button>
      </div>
    );
  }

  return children;
};

export default AdminRoute;
