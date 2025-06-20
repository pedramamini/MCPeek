import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css';

const blink = keyframes`
  50% { opacity: 0; }
`;

const TerminalWrapper = styled.div`
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  padding: 1rem;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
  border: 1px solid #00ff00;
  margin: 1rem;
  box-shadow: 
    inset 0 0 20px rgba(0, 255, 0, 0.1),
    0 0 20px rgba(0, 255, 0, 0.2);
`;

const OutputLine = styled(motion.div)`
  margin: 0.25rem 0;
  white-space: pre-wrap;
  word-break: break-all;
  
  &.command {
    color: #00ff00;
    font-weight: 600;
  }
  
  &.output {
    color: #00cc00;
    padding-left: 2rem;
  }
  
  &.error {
    color: #ff0040;
  }
  
  &.success {
    color: #00ff00;
    text-shadow: 0 0 5px #00ff00;
  }
  
  &.info {
    color: #0099ff;
  }
  
  &.prompt {
    color: #ffff00;
  }
`;

const InputLine = styled.div`
  display: flex;
  align-items: center;
  margin-top: 1rem;
  
  .prompt {
    color: #00ff00;
    margin-right: 0.5rem;
    font-weight: 600;
  }
`;

const CommandInput = styled.input`
  background: transparent;
  border: none;
  color: #00ff00;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  outline: none;
  flex: 1;
  caret-color: #00ff00;
  
  &::placeholder {
    color: #006600;
  }
`;

const Cursor = styled.span`
  background: #00ff00;
  width: 10px;
  height: 20px;
  display: inline-block;
  animation: ${blink} 1s infinite;
  margin-left: 2px;
`;

const SuggestionBox = styled.div`
  position: relative;
  
  .suggestions {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.95);
    border: 1px solid #00ff00;
    border-bottom: none;
    max-height: 200px;
    overflow-y: auto;
    z-index: 100;
    
    .suggestion {
      padding: 0.5rem;
      cursor: pointer;
      color: #00cc00;
      
      &:hover {
        background: rgba(0, 255, 0, 0.1);
        color: #00ff00;
      }
      
      &.selected {
        background: rgba(0, 255, 0, 0.2);
        color: #00ff00;
      }
    }
  }
`;

const JSONOutput = styled.div`
  .json-pretty {
    background: transparent !important;
    padding: 1rem 0;
    font-family: 'Fira Code', monospace !important;
    font-size: 12px !important;
    
    .json-string {
      color: #00ff00 !important;
    }
    
    .json-number {
      color: #0099ff !important;
    }
    
    .json-boolean {
      color: #ffff00 !important;
    }
    
    .json-null {
      color: #ff0040 !important;
    }
    
    .json-key {
      color: #ffffff !important;
    }
  }
`;

const COMMANDS = {
  help: 'Show available commands',
  discover: 'Discover MCP endpoint capabilities',
  tool: 'Execute an MCP tool',
  resource: 'Read an MCP resource',
  prompt: 'Get an MCP prompt',
  clear: 'Clear terminal',
  endpoint: 'Set current endpoint',
  auth: 'Set authentication',
  status: 'Show current status'
};

const Terminal = () => {
  const [output, setOutput] = useState([]);
  const [currentInput, setCurrentInput] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [currentEndpoint, setCurrentEndpoint] = useState('');
  const [currentAuth, setCurrentAuth] = useState({ apiKey: '', authHeader: '' });
  const [isExecuting, setIsExecuting] = useState(false);
  
  const inputRef = useRef(null);
  const terminalRef = useRef(null);
  
  useEffect(() => {
    // Initial welcome message
    addOutput('Welcome to MCPeek Web Terminal v1.0.0', 'success');
    addOutput('Type "help" for available commands', 'info');
    addOutput('');
    
    // Focus input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);
  
  useEffect(() => {
    // Auto-scroll to bottom
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);
  
  const addOutput = (text, type = 'output') => {
    setOutput(prev => [...prev, { text, type, id: Date.now() + Math.random() }]);
  };
  
  const executeCommand = async (command) => {
    if (!command.trim()) return;
    
    setIsExecuting(true);
    addOutput(`> ${command}`, 'command');
    
    const parts = command.trim().split(' ');
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    try {
      switch (cmd) {
        case 'help':
          addOutput('Available commands:', 'info');
          Object.entries(COMMANDS).forEach(([cmd, desc]) => {
            addOutput(`  ${cmd.padEnd(12)} - ${desc}`, 'output');
          });
          break;
          
        case 'clear':
          setOutput([]);
          break;
          
        case 'endpoint':
          if (args.length === 0) {
            addOutput(`Current endpoint: ${currentEndpoint || 'none'}`, 'info');
          } else {
            setCurrentEndpoint(args.join(' '));
            addOutput(`Endpoint set to: ${args.join(' ')}`, 'success');
          }
          break;
          
        case 'auth':
          if (args.length === 0) {
            addOutput('Usage: auth <api-key> or auth header <header>', 'info');
          } else if (args[0] === 'header') {
            setCurrentAuth(prev => ({ ...prev, authHeader: args.slice(1).join(' ') }));
            addOutput('Auth header set', 'success');
          } else {
            setCurrentAuth(prev => ({ ...prev, apiKey: args[0] }));
            addOutput('API key set', 'success');
          }
          break;
          
        case 'status':
          addOutput('Current Status:', 'info');
          addOutput(`  Endpoint: ${currentEndpoint || 'none'}`, 'output');
          addOutput(`  API Key: ${currentAuth.apiKey ? '***set***' : 'none'}`, 'output');
          addOutput(`  Auth Header: ${currentAuth.authHeader ? '***set***' : 'none'}`, 'output');
          break;
          
        case 'discover':
          await executeDiscover(args);
          break;
          
        case 'tool':
          await executeTool(args);
          break;
          
        case 'resource':
          await executeResource(args);
          break;
          
        case 'prompt':
          await executePrompt(args);
          break;
          
        default:
          addOutput(`Unknown command: ${cmd}`, 'error');
          addOutput('Type "help" for available commands', 'info');
      }
    } catch (error) {
      addOutput(`Error: ${error.message}`, 'error');
    }
    
    setIsExecuting(false);
  };
  
  const executeDiscover = async (args) => {
    if (!currentEndpoint) {
      addOutput('Error: No endpoint set. Use "endpoint <url>" first', 'error');
      return;
    }
    
    addOutput('Discovering endpoint capabilities...', 'info');
    
    try {
      const response = await axios.post('/api/discover', {
        endpoint: currentEndpoint,
        api_key: currentAuth.apiKey || null,
        auth_header: currentAuth.authHeader || null,
        verbosity: args.includes('-v') ? 1 : args.includes('-vv') ? 2 : args.includes('-vvv') ? 3 : 0,
        tool_tickle: args.includes('--tool-tickle')
      });
      
      if (response.data.success) {
        addOutput('Discovery completed successfully!', 'success');
        addOutput('');
        renderJSONOutput(response.data.data);
      } else {
        addOutput(`Discovery failed: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addOutput(`Network error: ${error.message}`, 'error');
    }
  };
  
  const executeTool = async (args) => {
    if (!currentEndpoint) {
      addOutput('Error: No endpoint set. Use "endpoint <url>" first', 'error');
      return;
    }
    
    if (args.length === 0) {
      addOutput('Usage: tool <tool_name> [json_parameters]', 'info');
      return;
    }
    
    const toolName = args[0];
    const parameters = args.length > 1 ? JSON.parse(args.slice(1).join(' ')) : null;
    
    addOutput(`Executing tool: ${toolName}`, 'info');
    
    try {
      const response = await axios.post('/api/execute/tool', {
        endpoint: currentEndpoint,
        api_key: currentAuth.apiKey || null,
        auth_header: currentAuth.authHeader || null,
        tool_name: toolName,
        parameters: parameters
      });
      
      if (response.data.success) {
        addOutput('Tool executed successfully!', 'success');
        addOutput('');
        renderJSONOutput(response.data.data);
      } else {
        addOutput(`Tool execution failed: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addOutput(`Network error: ${error.message}`, 'error');
    }
  };
  
  const executeResource = async (args) => {
    if (!currentEndpoint) {
      addOutput('Error: No endpoint set. Use "endpoint <url>" first', 'error');
      return;
    }
    
    if (args.length === 0) {
      addOutput('Usage: resource <resource_uri>', 'info');
      return;
    }
    
    const resourceUri = args.join(' ');
    
    addOutput(`Reading resource: ${resourceUri}`, 'info');
    
    try {
      const response = await axios.post('/api/execute/resource', {
        endpoint: currentEndpoint,
        api_key: currentAuth.apiKey || null,
        auth_header: currentAuth.authHeader || null,
        resource_uri: resourceUri
      });
      
      if (response.data.success) {
        addOutput('Resource read successfully!', 'success');
        addOutput('');
        renderJSONOutput(response.data.data);
      } else {
        addOutput(`Resource read failed: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addOutput(`Network error: ${error.message}`, 'error');
    }
  };
  
  const executePrompt = async (args) => {
    if (!currentEndpoint) {
      addOutput('Error: No endpoint set. Use "endpoint <url>" first', 'error');
      return;
    }
    
    if (args.length === 0) {
      addOutput('Usage: prompt <prompt_name> [json_parameters]', 'info');
      return;
    }
    
    const promptName = args[0];
    const parameters = args.length > 1 ? JSON.parse(args.slice(1).join(' ')) : null;
    
    addOutput(`Getting prompt: ${promptName}`, 'info');
    
    try {
      const response = await axios.post('/api/execute/prompt', {
        endpoint: currentEndpoint,
        api_key: currentAuth.apiKey || null,
        auth_header: currentAuth.authHeader || null,
        prompt_name: promptName,
        parameters: parameters
      });
      
      if (response.data.success) {
        addOutput('Prompt retrieved successfully!', 'success');
        addOutput('');
        renderJSONOutput(response.data.data);
      } else {
        addOutput(`Prompt retrieval failed: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addOutput(`Network error: ${error.message}`, 'error');
    }
  };
  
  const renderJSONOutput = (data) => {
    setOutput(prev => [...prev, { 
      text: <JSONOutput><JSONPretty data={data} /></JSONOutput>, 
      type: 'output', 
      id: Date.now() + Math.random(),
      isComponent: true 
    }]);
  };
  
  const handleInputChange = (e) => {
    const value = e.target.value;
    setCurrentInput(value);
    
    // Show suggestions
    if (value.trim()) {
      const matches = Object.keys(COMMANDS).filter(cmd => 
        cmd.toLowerCase().startsWith(value.toLowerCase())
      );
      setSuggestions(matches);
      setShowSuggestions(matches.length > 0);
      setSelectedSuggestion(0);
    } else {
      setShowSuggestions(false);
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (showSuggestions && suggestions.length > 0) {
        setCurrentInput(suggestions[selectedSuggestion]);
        setShowSuggestions(false);
      } else {
        executeCommand(currentInput);
        setCommandHistory(prev => [...prev, currentInput]);
        setCurrentInput('');
        setHistoryIndex(-1);
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (showSuggestions) {
        setSelectedSuggestion(prev => Math.max(0, prev - 1));
      } else if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setCurrentInput(commandHistory[newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (showSuggestions) {
        setSelectedSuggestion(prev => Math.min(suggestions.length - 1, prev + 1));
      } else if (historyIndex !== -1) {
        const newIndex = Math.min(commandHistory.length - 1, historyIndex + 1);
        if (newIndex === commandHistory.length - 1) {
          setHistoryIndex(-1);
          setCurrentInput('');
        } else {
          setHistoryIndex(newIndex);
          setCurrentInput(commandHistory[newIndex]);
        }
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      if (showSuggestions && suggestions.length > 0) {
        setCurrentInput(suggestions[selectedSuggestion]);
        setShowSuggestions(false);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };
  
  return (
    <TerminalWrapper ref={terminalRef}>
      <AnimatePresence>
        {output.map((item) => (
          <OutputLine
            key={item.id}
            className={item.type}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {item.isComponent ? item.text : item.text}
          </OutputLine>
        ))}
      </AnimatePresence>
      
      <SuggestionBox>
        {showSuggestions && suggestions.length > 0 && (
          <div className="suggestions">
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion}
                className={`suggestion ${index === selectedSuggestion ? 'selected' : ''}`}
                onClick={() => {
                  setCurrentInput(suggestion);
                  setShowSuggestions(false);
                  inputRef.current?.focus();
                }}
              >
                {suggestion} - {COMMANDS[suggestion]}
              </div>
            ))}
          </div>
        )}
        
        <InputLine>
          <span className="prompt">mcpeek@{currentEndpoint || 'localhost'}:~$</span>
          <CommandInput
            ref={inputRef}
            value={currentInput}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={isExecuting ? "Executing..." : "Enter command..."}
            disabled={isExecuting}
          />
          {!isExecuting && <Cursor />}
        </InputLine>
      </SuggestionBox>
    </TerminalWrapper>
  );
};

export default Terminal;