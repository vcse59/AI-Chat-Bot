import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTheme } from '../contexts/ThemeContext';
import { VERSION } from '../config/version';
import WorkflowTemplate from "../components/WorkflowTemplate";
import workflowService from "../services/workflowService";
import './WorkflowTemplates.css';

export default function WorkflowTemplates() {
  const [status, setStatus] = useState("");
  const navigate = useNavigate();
  const { theme, toggleTheme, isDark } = useTheme();

  const handleCreate = async config => {
    setStatus("Creating workflow...");
    try {
      const result = await workflowService.createWorkflow(config);
      setStatus("Workflow created successfully! Redirecting to chat...");
      // Notify chat page to refresh conversations via localStorage
      localStorage.setItem('conversationChanged', JSON.stringify({ action: 'created', timestamp: Date.now() }));
      // Redirect to chat page after a brief delay to show success message
      setTimeout(() => {
        navigate('/chat');
      }, 1000);
    } catch (err) {
      setStatus("Error: " + err);
    }
  };

  const handleBackToChat = () => {
    navigate('/chat');
  };

  return (
    <div className="workflow-page-bg">
      <div className="workflow-page-header">
        <button onClick={handleBackToChat} className="back-to-chat-button">
          ← Back to Chat
        </button>
        <button onClick={toggleTheme} className="theme-toggle-btn" title={`Switch to ${isDark ? 'light' : 'dark'} mode`}>
          {isDark ? '☀️ Light' : '🌙 Dark'}
        </button>
        <div className="header-logo">
          <span className="logo-icon">💬</span>
          <span className="logo-text">ConvoAI</span>
          <span className="version-badge">v{VERSION}</span>
        </div>
        <h1>🧩 LangChain Workflows</h1>
        <p className="workflow-page-desc">Create and manage AI-powered workflows. Select a template, customize prompts, and launch new workflows instantly.</p>
      </div>
      <WorkflowTemplate onCreate={handleCreate} />
      {status && <div className={`workflow-status ${status.startsWith('Error') ? 'error' : 'success'}`}>{status}</div>}
    </div>
  );
}
