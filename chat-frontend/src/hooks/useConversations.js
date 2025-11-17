import { useState, useEffect } from 'react';
import chatService from '../services/chatService';

export const useConversations = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadConversations = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      setError(null);
      const data = await chatService.getConversations();
      setConversations(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading conversations:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();

    // Listen for external conversation changes (e.g., admin deletions)
    const handleExternalConversationChange = (event) => {
      const { action, conversationId } = event.detail;
      
      if (action === 'deleted') {
        // Remove conversation from list without API call
        setConversations(prev => prev.filter(c => c.id !== conversationId));
      } else {
        // For other actions, silently refresh the list
        loadConversations(true);
      }
    };

    window.addEventListener('conversationDeleted', handleExternalConversationChange);

    return () => {
      window.removeEventListener('conversationDeleted', handleExternalConversationChange);
    };
  }, []);

  const createConversation = async (title) => {
    try {
      setError(null);
      const newConversation = await chatService.createConversation(title);
      setConversations(prev => [newConversation, ...prev]);
      
      // Trigger analytics update event
      window.dispatchEvent(new CustomEvent('conversationChanged', { 
        detail: { action: 'created', conversationId: newConversation.id }
      }));
      
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
      
      // Trigger analytics update event
      window.dispatchEvent(new CustomEvent('conversationChanged', { 
        detail: { action: 'deleted', conversationId }
      }));
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
      
      // Trigger analytics update event
      window.dispatchEvent(new CustomEvent('conversationChanged', { 
        detail: { action: 'updated', conversationId }
      }));
      
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
