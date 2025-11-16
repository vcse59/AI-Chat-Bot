import authService from './authService';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.messageHandlers = [];
    this.connectionHandlers = [];
    this.errorHandlers = [];
    this.currentConversationId = null;
  }

  /**
   * Connect to WebSocket server
   * @param {string} conversationId - Conversation hash ID
   * @param {boolean} isReconnect - If true, this is a reconnection attempt
   */
  connect(conversationId, isReconnect = false) {
    const token = authService.getToken();
    if (!token) {
      console.error('No authentication token found');
      return;
    }

    // If connecting to a new conversation (not a reconnect), reset reconnect attempts
    if (!isReconnect || conversationId !== this.currentConversationId) {
      this.reconnectAttempts = 0;
    }

    this.currentConversationId = conversationId;
    const wsUrl = `${WS_URL}/ws/${conversationId}?token=${token}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this._notifyConnectionHandlers('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._notifyMessageHandlers(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this._notifyErrorHandlers(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this._notifyConnectionHandlers('disconnected');
        this._attemptReconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      this._notifyErrorHandlers(error);
    }
  }

  /**
   * Send a message through WebSocket
   * @param {string} message - Message content
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const data = {
        type: 'send_message',
        data: {
          conversation_id: this.currentConversationId,
          content: message,
        }
      };
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
      this._notifyErrorHandlers(new Error('WebSocket is not connected'));
    }
  }

  /**
   * Disconnect from WebSocket server
   * @param {boolean} preventReconnect - If true, prevents automatic reconnection
   */
  disconnect(preventReconnect = true) {
    if (preventReconnect) {
      this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.currentConversationId = null;
  }

  /**
   * Register a message handler
   * @param {function} handler - Callback function to handle messages
   * @returns {function} - Unsubscribe function
   */
  onMessage(handler) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  /**
   * Register a connection status handler
   * @param {function} handler - Callback function to handle connection status
   * @returns {function} - Unsubscribe function
   */
  onConnection(handler) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }

  /**
   * Register an error handler
   * @param {function} handler - Callback function to handle errors
   * @returns {function} - Unsubscribe function
   */
  onError(handler) {
    this.errorHandlers.push(handler);
    return () => {
      this.errorHandlers = this.errorHandlers.filter(h => h !== handler);
    };
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean}
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Attempt to reconnect to WebSocket
   * @private
   */
  _attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.currentConversationId) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => {
        this.connect(this.currentConversationId, true); // Pass true to indicate reconnect
      }, this.reconnectDelay);
    } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this._notifyErrorHandlers(new Error('Failed to reconnect after maximum attempts'));
      // Reset for future connections
      this.reconnectAttempts = 0;
    }
  }

  /**
   * Notify all message handlers
   * @private
   */
  _notifyMessageHandlers(data) {
    this.messageHandlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error('Error in message handler:', error);
      }
    });
  }

  /**
   * Notify all connection handlers
   * @private
   */
  _notifyConnectionHandlers(status) {
    this.connectionHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('Error in connection handler:', error);
      }
    });
  }

  /**
   * Notify all error handlers
   * @private
   */
  _notifyErrorHandlers(error) {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (error) {
        console.error('Error in error handler:', error);
      }
    });
  }
}

export default new WebSocketService();
