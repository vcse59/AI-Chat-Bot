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

    // Check if there was a recent workflow creation (for same-tab navigation)
    const lastChange = localStorage.getItem('conversationChanged');
    if (lastChange) {
      try {
        const parsed = JSON.parse(lastChange);
        // If the change was within the last 5 seconds, refresh
        if (parsed.timestamp && Date.now() - parsed.timestamp < 5000) {
          loadConversations(true);
        }
      } catch (e) {
        // Ignore parse errors
      }
      // Clear the flag after processing
      localStorage.removeItem('conversationChanged');
    }

    // Listen for external conversation changes (e.g., admin deletions, workflow creations)
    const handleExternalConversationChange = (event) => {
      const { action, conversationId } = event.detail;
      
      if (action === 'deleted') {
        // Remove conversation from list without API call
        setConversations(prev => prev.filter(c => c.id !== conversationId));
      } else {
        // For other actions (created, updated), silently refresh the list
        loadConversations(true);
      }
    };

    window.addEventListener('conversationDeleted', handleExternalConversationChange);
    window.addEventListener('conversationChanged', handleExternalConversationChange);

    // Listen for cross-tab conversation changes via localStorage
    const handleStorageChange = (event) => {
      if (event.key === 'conversationChanged') {
        loadConversations(true);
      }
    };
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('conversationDeleted', handleExternalConversationChange);
      window.removeEventListener('conversationChanged', handleExternalConversationChange);
      window.removeEventListener('storage', handleStorageChange);
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
