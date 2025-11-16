import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ConversationList from '../components/ConversationList';
import ChatWindow from '../components/ChatWindow';
import './ChatPage.css';

const ChatPage = () => {
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h1>Chat Application</h1>
        <div className="user-info">
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
        />
        <ChatWindow conversationId={selectedConversationId} />
      </div>
    </div>
  );
};

export default ChatPage;
