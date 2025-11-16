import React from 'react';
import './MessageList.css';

const MessageList = ({ messages }) => {
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (messages.length === 0) {
    return (
      <div className="no-messages">
        <p>No messages yet. Start the conversation!</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <div
          key={message.id || index}
          className={`message ${message.role === 'user' ? 'message-user' : 'message-assistant'}`}
        >
          <div className="message-header">
            <span className="message-role">
              {message.role === 'user' ? '👤 You' : '🤖 Assistant'}
            </span>
            {message.created_at && (
              <span className="message-time">{formatTime(message.created_at)}</span>
            )}
          </div>
          <div className="message-content">{message.content}</div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;
