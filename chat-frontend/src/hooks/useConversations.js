import { useState, useEffect } from 'react';
import chatService from '../services/chatService';

export const useConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await chatService.getConversations();
      setConversations(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const createConversation = async (title) => {
    try {
      setError(null);
      const newConversation = await chatService.createConversation(title);
      setConversations(prev => [newConversation, ...prev]);
      return newConversation;
    } catch (err) {
      setError(err.message);
      console.error('Error creating conversation:', err);
      throw err;
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      setError(null);
      await chatService.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
    } catch (err) {
      setError(err.message);
      console.error('Error deleting conversation:', err);
      throw err;
    }
  };

  const updateConversation = async (conversationId, data) => {
    try {
      setError(null);
      const updated = await chatService.updateConversation(conversationId, data);
      setConversations(prev => prev.map(c => c.id === conversationId ? updated : c));
      return updated;
    } catch (err) {
      setError(err.message);
      console.error('Error updating conversation:', err);
      throw err;
    }
  };

  return {
    conversations,
    loading,
    error,
    createConversation,
    deleteConversation,
    updateConversation,
    refreshConversations: loadConversations,
  };
};
