import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled, { keyframes } from 'styled-components';
import axios from 'axios';

interface TerminalProps {
  onEndpointChange: (endpoint: string) => void;
  currentEndpoint: string;
}

interface HistoryEntry {
  command: string;
  output: string;
  timestamp: Date;
  success: boolean;
}

interface MCPState {
  endpoint: string;
  apiKey: string;
  authHeader: string;
  timeout: number;
}

const blink = keyframes`
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
`;

const TerminalContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff00;
  margin: 10px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 
    0 0 20px rgba(0, 255, 0, 0.3),
    inset 0 0 20px rgba(0, 255, 0, 0.1);
`;

const TerminalHeader = styled.div`
  background: linear-gradient(90deg, #002200 0%, #004400 50%, #002200 100%);
  padding: 8px 15px;
  border-bottom: 1px solid #00ff00;
  font-size: 12px;
  color: #00cc00;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const WindowControls = styled.div`
  display: flex;
  gap: 6px;
  
  .control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 1px solid #00ff00;
    background: rgba(0, 255, 0, 0.2);
    
    &:hover {
      background: rgba(0, 255, 0, 0.4);
    }
  }
`;

const TerminalOutput = styled.div`
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: radial-gradient(ellipse at center, rgba(0, 20, 0, 0.4) 0%, rgba(0, 0, 0, 0.8) 100%);
`;

const HistoryEntry = styled.div<{ success: boolean }>`
  margin-bottom: 15px;
  
  .command {
    color: #00ffff;
    font-weight: 600;
    margin-bottom: 5px;
    
    &::before {
      content: '$ ';
      color: #00ff00;
    }
  }
  
  .output {
    color: ${props => props.success ? '#00ff00' : '#ff4444'};
    white-space: pre-wrap;
    margin-left: 15px;
    padding: 10px;
    background: rgba(0, 0, 0, 0.6);
    border-left: 3px solid ${props => props.success ? '#00ff00' : '#ff4444'};
    border-radius: 0 4px 4px 0;
    font-size: 12px;
  }
  
  .timestamp {
    color: #006600;
    font-size: 10px;
    margin-top: 5px;
    margin-left: 15px;
  }
`;

const InputContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 15px;
  border-top: 1px solid #00ff00;
  background: rgba(0, 30, 0, 0.8);
`;

const Prompt = styled.span`
  color: #00ff00;
  font-weight: 600;
  margin-right: 8px;
  text-shadow: 0 0 5px #00ff00;
`;

const Input = styled.input`
  flex: 1;
  background: transparent;
  border: none;
  color: #00ffff;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  outline: none;
  caret-color: #00ff00;
  
  &::placeholder {
    color: #006600;
  }
`;

const Cursor = styled.span`
  color: #00ff00;
  animation: ${blink} 1s infinite;
  margin-left: 2px;
`;

const HelpPanel = styled.div`
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff00;
  padding: 15px;
  font-size: 11px;
  max-width: 300px;
  z-index: 100;
  border-radius: 4px;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  
  .help-title {
    color: #00ff00;
    font-weight: 600;
    margin-bottom: 10px;
    text-align: center;
  }
  
  .help-command {
    color: #00ffff;
    margin: 5px 0;
    
    .cmd {
      color: #00ff00;
      font-weight: 600;
    }
    
    .desc {
      color: #00cc00;
      margin-left: 10px;
    }
  }
`;

const Terminal: React.FC<TerminalProps> = ({ onEndpointChange, currentEndpoint }) => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [mcpState, setMcpState] = useState<MCPState>({
    endpoint: '',
    apiKey: '',
    authHeader: '',
    timeout: 30.0
  });

  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  const commands = [
    { cmd: 'endpoint <url>', desc: 'Set MCP endpoint URL' },
    { cmd: 'discover [-v|-vv|-vvv]', desc: 'Explore endpoint capabilities' },
    { cmd: 'tool <name> [params]', desc: 'Execute MCP tool' },
    { cmd: 'resource <uri>', desc: 'Read MCP resource' },
    { cmd: 'prompt <name> [params]', desc: 'Get MCP prompt' },
    { cmd: 'auth <api-key>', desc: 'Set API key' },
    { cmd: 'header <header>', desc: 'Set auth header' },
    { cmd: 'timeout <seconds>', desc: 'Set connection timeout' },
    { cmd: 'status', desc: 'Show current settings' },
    { cmd: 'clear', desc: 'Clear terminal' },
    { cmd: 'help', desc: 'Show this help' },
  ];

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [history]);

  const addToHistory = useCallback((command: string, output: string, success: boolean = true) => {
    const entry: HistoryEntry = {
      command,
      output,
      timestamp: new Date(),
      success
    };
    setHistory(prev => [...prev, entry]);
  }, []);

  const executeCommand = async (command: string) => {
    if (!command.trim()) return;

    setIsProcessing(true);
    const parts = command.trim().split(' ');
    const cmd = parts[0].toLowerCase();

    try {
      switch (cmd) {
        case 'help':
          setShowHelp(!showHelp);
          addToHistory(command, 'Help panel toggled');
          break;

        case 'clear':
          setHistory([]);
          break;

        case 'endpoint':
          if (parts.length < 2) {
            addToHistory(command, 'Usage: endpoint <url>', false);
          } else {
            const endpoint = parts.slice(1).join(' ');
            setMcpState(prev => ({ ...prev, endpoint }));
            onEndpointChange(endpoint);
            addToHistory(command, `Endpoint set to: ${endpoint}`);
          }
          break;

        case 'auth':
          if (parts.length < 2) {
            addToHistory(command, 'Usage: auth <api-key>', false);
          } else {
            const apiKey = parts[1];
            setMcpState(prev => ({ ...prev, apiKey }));
            addToHistory(command, 'API key set successfully');
          }
          break;

        case 'header':
          if (parts.length < 2) {
            addToHistory(command, 'Usage: header <auth-header>', false);
          } else {
            const authHeader = parts.slice(1).join(' ');
            setMcpState(prev => ({ ...prev, authHeader }));
            addToHistory(command, 'Auth header set successfully');
          }
          break;

        case 'timeout':
          if (parts.length < 2) {
            addToHistory(command, 'Usage: timeout <seconds>', false);
          } else {
            const timeout = parseFloat(parts[1]);
            if (isNaN(timeout) || timeout <= 0) {
              addToHistory(command, 'Invalid timeout value', false);
            } else {
              setMcpState(prev => ({ ...prev, timeout }));
              addToHistory(command, `Timeout set to: ${timeout} seconds`);
            }
          }
          break;

        case 'status':
          const status = `Current Settings:
Endpoint: ${mcpState.endpoint || 'Not set'}
API Key: ${mcpState.apiKey ? '***set***' : 'Not set'}
Auth Header: ${mcpState.authHeader ? '***set***' : 'Not set'}
Timeout: ${mcpState.timeout} seconds`;
          addToHistory(command, status);
          break;

        case 'discover':
          if (!mcpState.endpoint) {
            addToHistory(command, 'No endpoint set. Use: endpoint <url>', false);
            break;
          }

          const verbosity = parts.includes('-vvv') ? 3 : 
                          parts.includes('-vv') ? 2 : 
                          parts.includes('-v') ? 1 : 0;

          const toolTickle = parts.includes('--tool-tickle');

          const discoverResult = await axios.post('/api/discover', {
            endpoint: mcpState.endpoint,
            api_key: mcpState.apiKey || null,
            auth_header: mcpState.authHeader || null,
            timeout: mcpState.timeout,
            verbosity,
            tool_tickle: toolTickle
          });

          addToHistory(command, discoverResult.data.raw_output);
          break;

        case 'tool':
          if (!mcpState.endpoint) {
            addToHistory(command, 'No endpoint set. Use: endpoint <url>', false);
            break;
          }
          if (parts.length < 2) {
            addToHistory(command, 'Usage: tool <name> [json-params]', false);
            break;
          }

          const toolName = parts[1];
          let inputData = null;

          if (parts.length > 2) {
            try {
              inputData = JSON.parse(parts.slice(2).join(' '));
            } catch (e) {
              addToHistory(command, 'Invalid JSON parameters', false);
              break;
            }
          }

          const toolResult = await axios.post('/api/tool', {
            endpoint: mcpState.endpoint,
            api_key: mcpState.apiKey || null,
            auth_header: mcpState.authHeader || null,
            timeout: mcpState.timeout,
            tool_name: toolName,
            input_data: inputData
          });

          addToHistory(command, toolResult.data.raw_output);
          break;

        case 'resource':
          if (!mcpState.endpoint) {
            addToHistory(command, 'No endpoint set. Use: endpoint <url>', false);
            break;
          }
          if (parts.length < 2) {
            addToHistory(command, 'Usage: resource <uri>', false);
            break;
          }

          const resourceUri = parts.slice(1).join(' ');
          const resourceResult = await axios.post('/api/resource', {
            endpoint: mcpState.endpoint,
            api_key: mcpState.apiKey || null,
            auth_header: mcpState.authHeader || null,
            timeout: mcpState.timeout,
            resource_uri: resourceUri
          });

          addToHistory(command, resourceResult.data.raw_output);
          break;

        case 'prompt':
          if (!mcpState.endpoint) {
            addToHistory(command, 'No endpoint set. Use: endpoint <url>', false);
            break;
          }
          if (parts.length < 2) {
            addToHistory(command, 'Usage: prompt <name> [json-params]', false);
            break;
          }

          const promptName = parts[1];
          let promptInputData = null;

          if (parts.length > 2) {
            try {
              promptInputData = JSON.parse(parts.slice(2).join(' '));
            } catch (e) {
              addToHistory(command, 'Invalid JSON parameters', false);
              break;
            }
          }

          const promptResult = await axios.post('/api/prompt', {
            endpoint: mcpState.endpoint,
            api_key: mcpState.apiKey || null,
            auth_header: mcpState.authHeader || null,
            timeout: mcpState.timeout,
            prompt_name: promptName,
            input_data: promptInputData
          });

          addToHistory(command, promptResult.data.raw_output);
          break;

        default:
          addToHistory(command, `Unknown command: ${cmd}. Type 'help' for available commands.`, false);
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error occurred';
      addToHistory(command, `Error: ${errorMsg}`, false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isProcessing) {
      executeCommand(input);
      setHistoryIndex(-1);
      setInput('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (history.length > 0) {
        const newIndex = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
        setHistoryIndex(newIndex);
        setInput(history[newIndex].command);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex >= 0) {
        const newIndex = historyIndex + 1;
        if (newIndex >= history.length) {
          setHistoryIndex(-1);
          setInput('');
        } else {
          setHistoryIndex(newIndex);
          setInput(history[newIndex].command);
        }
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // Simple command completion
      const currentInput = input.toLowerCase();
      const matches = commands.filter(cmd => cmd.cmd.toLowerCase().startsWith(currentInput));
      if (matches.length === 1) {
        setInput(matches[0].cmd.split(' ')[0]);
      }
    }
  };

  return (
    <TerminalContainer>
      <TerminalHeader>
        <span>MCPeek Terminal - {currentEndpoint || 'No endpoint'}</span>
        <WindowControls>
          <div className="control" />
          <div className="control" />
          <div className="control" />
        </WindowControls>
      </TerminalHeader>

      <TerminalOutput ref={outputRef}>
        {history.map((entry, index) => (
          <HistoryEntry key={index} success={entry.success}>
            <div className="command">{entry.command}</div>
            <div className="output">{entry.output}</div>
            <div className="timestamp">
              [{entry.timestamp.toLocaleTimeString()}]
            </div>
          </HistoryEntry>
        ))}
        {isProcessing && (
          <div style={{ color: '#ffff00', margin: '10px 0' }}>
            Processing... <Cursor>█</Cursor>
          </div>
        )}
      </TerminalOutput>

      <InputContainer>
        <Prompt>mcpeek@terminal:~$</Prompt>
        <Input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter command... (type 'help' for available commands)"
          disabled={isProcessing}
        />
        <Cursor>█</Cursor>
      </InputContainer>

      {showHelp && (
        <HelpPanel>
          <div className="help-title">Available Commands</div>
          {commands.map((cmd, index) => (
            <div key={index} className="help-command">
              <span className="cmd">{cmd.cmd}</span>
              <div className="desc">{cmd.desc}</div>
            </div>
          ))}
        </HelpPanel>
      )}
    </TerminalContainer>
  );
};

export default Terminal;