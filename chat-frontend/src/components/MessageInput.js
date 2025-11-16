import React from 'react';
import './MessageInput.css';

const MessageInput = ({ value, onChange, onSend, disabled, placeholder }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend(e);
    }
  };

  return (
    <form onSubmit={onSend} className="message-input-container">
      <div className="message-input-wrapper">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder || 'Type your message...'}
          disabled={disabled}
          rows={1}
          className="message-input"
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="send-button"
          title="Send message"
        >
          📤
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
