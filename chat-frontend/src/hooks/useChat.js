import { useState, useEffect, useCallback } from 'react';
import chatService from '../services/chatService';
import websocketService from '../services/websocketService';

export const useChat = (conversationId) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  const [sending, setSending] = useState(false);

  // Load messages when conversation changes
  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      setLoading(false);
      return;
    }

    const loadMessages = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await chatService.getMessages(conversationId);
        setMessages(data);
      } catch (err) {
        setError(err.message);
        console.error('Error loading messages:', err);
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, [conversationId]);

  // Setup WebSocket connection
  useEffect(() => {
    if (!conversationId) return;

    // Connect to WebSocket
    websocketService.connect(conversationId);

    // Handle incoming messages
    const unsubscribeMessage = websocketService.onMessage((data) => {
      console.log('WebSocket message received:', data);
      
      // Handle different message types
      if (data.type === 'send_message' && data.success && data.data) {
        // Backend sends both user_message and ai_response
        const { user_message, ai_response } = data.data;
        
        setMessages(prev => {
          // Remove optimistic user message if exists
          const withoutOptimistic = prev.filter(msg => !msg.optimistic);
          
          // Add confirmed user message and AI response
          return [
            ...withoutOptimistic,
            {
              role: 'user',
              content: user_message.content,
              conversation_id: conversationId,
              created_at: user_message.timestamp,
              id: user_message.id
            },
            {
              role: 'assistant',
              content: ai_response.content,
              conversation_id: conversationId,
              created_at: ai_response.timestamp,
              id: ai_response.id,
              tokens_used: ai_response.tokens_used
            }
          ];
        });
      } else if (data.type === 'message_broadcast' && data.data) {
        // Handle broadcast messages from other clients
        const { user_message, ai_response } = data.data;
        
        setMessages(prev => [
          ...prev,
          {
            role: 'user',
            content: user_message.content,
            conversation_id: conversationId,
            created_at: user_message.timestamp,
            id: user_message.id
          },
          {
            role: 'assistant',
            content: ai_response.content,
            conversation_id: conversationId,
            created_at: ai_response.timestamp,
            id: ai_response.id,
            tokens_used: ai_response.tokens_used
          }
        ]);
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.error);
        setError(data.error);
      }
    });

    // Handle connection status
    const unsubscribeConnection = websocketService.onConnection((status) => {
      setConnected(status === 'connected');
    });

    // Handle errors
    const unsubscribeError = websocketService.onError((err) => {
      console.error('WebSocket error:', err);
      setError(err.message);
    });

    // Cleanup on unmount or conversation change
    return () => {
      unsubscribeMessage();
      unsubscribeConnection();
      unsubscribeError();
      // Disconnect but allow future connections (pass false to preventReconnect)
      websocketService.disconnect(false);
    };
  }, [conversationId]);

  // Send message function
  const sendMessage = useCallback(async (content) => {
    if (!conversationId || !content.trim()) return;

    try {
      setSending(true);
      setError(null);

      // If WebSocket is connected, use it for real-time messaging
      if (websocketService.isConnected()) {
        // Add optimistic user message to UI immediately
        const userMessage = {
          role: 'user',
          content: content,
          conversation_id: conversationId,
          created_at: new Date().toISOString(),
          optimistic: true // Mark as optimistic for removal on confirmation
        };
        setMessages(prev => [...prev, userMessage]);
        
        // Send via WebSocket
        websocketService.send(content);
      } else {
        // Fallback to HTTP API
        const message = await chatService.sendMessage(conversationId, content, 'user');
        setMessages(prev => [...prev, message]);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error sending message:', err);
      throw err;
    } finally {
      setSending(false);
    }
  }, [conversationId]);

  return {
    messages,
    loading,
    error,
    connected,
    sending,
    sendMessage,
  };
};
