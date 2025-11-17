import React, { useState } from 'react';
import { useConversations } from '../hooks/useConversations';
import './ConversationList.css';

const ConversationList = ({ selectedConversationId, onSelectConversation, onConversationDeleted }) => {
  const { conversations, loading, error, createConversation, deleteConversation } = useConversations();
  const [newConversationTitle, setNewConversationTitle] = useState('');
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [creating, setCreating] = useState(false);

  const handleCreateConversation = async (e) => {
    e.preventDefault();
    if (!newConversationTitle.trim()) return;

    setCreating(true);
    try {
      const newConv = await createConversation(newConversationTitle);
      setNewConversationTitle('');
      setShowNewConversation(false);
      onSelectConversation(newConv.id);
    } catch (err) {
      console.error('Failed to create conversation:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await deleteConversation(conversationId);
        if (selectedConversationId === conversationId) {
          onSelectConversation(null);
        }
        // Notify parent component that a conversation was deleted
        if (onConversationDeleted) {
          onConversationDeleted();
        }
      } catch (err) {
        console.error('Failed to delete conversation:', err);
      }
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="conversation-list">
        <div className="conversation-list-header">
          <h2>Conversations</h2>
        </div>
        <div className="loading">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h2>Conversations</h2>
        <button
          onClick={() => setShowNewConversation(!showNewConversation)}
          className="new-conversation-button"
          title="New Conversation"
        >
          ➕
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showNewConversation && (
        <form onSubmit={handleCreateConversation} className="new-conversation-form">
          <input
            type="text"
            placeholder="Conversation title..."
            value={newConversationTitle}
            onChange={(e) => setNewConversationTitle(e.target.value)}
            disabled={creating}
            autoFocus
          />
          <div className="form-buttons">
            <button type="submit" disabled={creating || !newConversationTitle.trim()}>
              {creating ? 'Creating...' : 'Create'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowNewConversation(false);
                setNewConversationTitle('');
              }}
              disabled={creating}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="conversations-container">
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No conversations yet</p>
            <p className="hint">Click ➕ to start a new conversation</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${selectedConversationId === conv.id ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-info">
                <div className="conversation-title">{conv.title}</div>
                <div className="conversation-date">{formatDate(conv.updated_at)}</div>
              </div>
              <button
                className="delete-conversation-button"
                onClick={(e) => handleDeleteConversation(conv.id, e)}
                title="Delete conversation"
              >
                🗑️
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationList;
