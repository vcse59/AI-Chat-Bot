import React, { useState } from "react";
import './WorkflowTemplate.css';

const workflowPresets = [
  {
    name: "Basic Conversation",
    description: "A simple conversation workflow using LangChain's ConversationChain.",
    config: {
      chainType: "ConversationChain",
      memory: "ConversationBufferMemory",
      prompt: "Default system prompt"
    }
  },
  {
    name: "LLM Chain with Custom Prompt",
    description: "LLMChain workflow with customizable prompt.",
    config: {
      chainType: "LLMChain",
      memory: "None",
      prompt: "Custom prompt"
    }
  }
];

export default function WorkflowTemplate({ onCreate }) {
  const [selected, setSelected] = useState(null);
  const [customPrompt, setCustomPrompt] = useState("");

  const handleSelect = idx => {
    setSelected(idx);
    setCustomPrompt("");
  };

  const handleCreate = () => {
    let config = { ...workflowPresets[selected].config };
    if (config.prompt === "Custom prompt") config.prompt = customPrompt;
    onCreate && onCreate(config);
  };

  return (
    <div className="workflow-template">
      <h2>Add LangChain Workflow Template</h2>
      <ul>
        {workflowPresets.map((preset, idx) => (
          <li key={preset.name} className={selected === idx ? "selected" : ""} onClick={() => handleSelect(idx)}>
            <strong>{preset.name}</strong>
            <p>{preset.description}</p>
          </li>
        ))}
      </ul>
      {selected !== null && workflowPresets[selected].config.prompt === "Custom prompt" && (
        <div className="custom-prompt">
          <label>Custom Prompt:</label>
          <input value={customPrompt} onChange={e => setCustomPrompt(e.target.value)} placeholder="Enter your prompt..." />
        </div>
      )}
      {selected !== null && (
        <button onClick={handleCreate} className="create-btn">Create Workflow</button>
      )}
    </div>
  );
}
