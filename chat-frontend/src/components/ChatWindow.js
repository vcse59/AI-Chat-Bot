import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatWindow.css';

const ChatWindow = ({ conversationId }) => {
  const { messages, loading, error, connected, sending, sendMessage } = useChat(conversationId);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || sending) return;

    const messageContent = inputValue;
    setInputValue('');

    try {
      await sendMessage(messageContent);
    } catch (err) {
      console.error('Failed to send message:', err);
      // Restore input value on error
      setInputValue(messageContent);
    }
  };

  if (!conversationId) {
    return (
      <div className="chat-window">
        <div className="no-conversation-selected">
          <div className="welcome-message">
            <h2>👋 Welcome to Chat Application</h2>
            <p>Select a conversation from the sidebar to start chatting</p>
            <p>or create a new conversation to get started</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-window-header">
        <div className="connection-status">
          {connected ? (
            <span className="status-connected">🟢 Connected</span>
          ) : (
            <span className="status-disconnected">🔴 Disconnected</span>
          )}
        </div>
      </div>

      <div className="messages-container">
        {loading && messages.length === 0 ? (
          <div className="loading-messages">Loading messages...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <>
            <MessageList messages={messages} />
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <MessageInput
        value={inputValue}
        onChange={setInputValue}
        onSend={handleSendMessage}
        disabled={sending}
        placeholder={sending ? 'Sending...' : 'Type your message...'}
      />
    </div>
  );
};

export default ChatWindow;
