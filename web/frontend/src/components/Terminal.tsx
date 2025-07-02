import React, { useState, useEffect, useRef, useCallback } from 'react'
import styled from 'styled-components'
import StatusBar from './StatusBar'
import { executeCommand, CommandResult } from '../services/api'

const TerminalContainer = styled.div`
  flex: 1;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
`

const TerminalContent = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.4;
  display: flex;
  flex-direction: column;
`

const OutputLine = styled.div<{ type?: 'command' | 'output' | 'error' | 'info' | 'success' }>`
  margin: 2px 0;
  color: ${props => {
    switch (props.type) {
      case 'command': return '#00ffff'
      case 'error': return '#ff0000'
      case 'info': return '#ffff00'
      case 'success': return '#00ff00'
      default: return '#00cc00'
    }
  }};
  word-wrap: break-word;
  white-space: pre-wrap;
  text-shadow: ${props => props.type === 'command' ? '0 0 5px currentColor' : 'none'};
  
  &.slide-in {
    animation: slideIn 0.3s ease-out;
  }
`

const InputContainer = styled.div`
  display: flex;
  align-items: center;
  margin-top: 10px;
  border-top: 1px solid #00ff00;
  padding-top: 10px;
`

const Prompt = styled.span`
  color: #00ff00;
  margin-right: 10px;
  font-weight: bold;
  text-shadow: 0 0 5px #00ff00;
  white-space: nowrap;
`

const Input = styled.input`
  flex: 1;
  background: transparent;
  border: none;
  color: #00ff00;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  outline: none;
  padding: 5px;
  caret-color: #00ff00;
  
  &::placeholder {
    color: #006600;
  }
`

const HelpPanel = styled.div<{ visible: boolean }>`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 15px;
  display: ${props => props.visible ? 'block' : 'none'};
  z-index: 20;
  font-size: 12px;
  box-shadow: 0 0 10px #00ff00;
`

const HelpTitle = styled.div`
  color: #00ff00;
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
  text-shadow: 0 0 5px #00ff00;
`

const HelpCommand = styled.div`
  margin: 5px 0;
  display: flex;
  
  .command {
    color: #00ffff;
    min-width: 120px;
  }
  
  .description {
    color: #00cc00;
  }
`

interface TerminalState {
  output: Array<{ id: number; content: string; type: 'command' | 'output' | 'error' | 'info' | 'success' }>
  currentInput: string
  commandHistory: string[]
  historyIndex: number
  currentEndpoint: string
  apiKey: string
  authHeader: string
  showHelp: boolean
  isExecuting: boolean
  commandCount: number
}

const Terminal: React.FC = () => {
  const [state, setState] = useState<TerminalState>({
    output: [
      { id: 0, content: '🚀 MCPeek Hacker Terminal Interface v1.0.0', type: 'info' },
      { id: 1, content: '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', type: 'info' },
      { id: 2, content: '⚡ Welcome to the matrix of MCP exploration', type: 'success' },
      { id: 3, content: '💀 Type "help" to see available commands or start hacking with "endpoint <url>"', type: 'info' },
      { id: 4, content: '🎯 Ready to hack the gibson...', type: 'success' },
      { id: 5, content: '', type: 'output' }
    ],
    currentInput: '',
    commandHistory: [],
    historyIndex: -1,
    currentEndpoint: '',
    apiKey: '',
    authHeader: '',
    showHelp: false,
    isExecuting: false,
    commandCount: 0
  })

  const inputRef = useRef<HTMLInputElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const outputIdRef = useRef(6)

  // Auto-focus input
  useEffect(() => {
    if (inputRef.current && !state.isExecuting) {
      inputRef.current.focus()
    }
  }, [state.isExecuting])

  // Auto-scroll to bottom
  useEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [state.output])

  const addOutput = useCallback((content: string, type: 'command' | 'output' | 'error' | 'info' | 'success' = 'output') => {
    setState(prev => ({
      ...prev,
      output: [...prev.output, { id: outputIdRef.current++, content, type }]
    }))
  }, [])

  const commands = {
    help: () => {
      setState(prev => ({ ...prev, showHelp: !prev.showHelp }))
      addOutput('Help panel toggled', 'info')
    },
    
    clear: () => {
      setState(prev => ({
        ...prev,
        output: [
          { id: outputIdRef.current++, content: '🚀 Terminal cleared - Ready for new commands', type: 'info' }
        ]
      }))
    },
    
    endpoint: (url: string) => {
      if (!url) {
        addOutput('Usage: endpoint <url>', 'error')
        addOutput('Example: endpoint http://localhost:8000/mcp', 'info')
        return
      }
      setState(prev => ({ ...prev, currentEndpoint: url }))
      addOutput(`Endpoint set to: ${url}`, 'success')
    },
    
    auth: (key: string) => {
      if (!key) {
        addOutput('Usage: auth <api-key>', 'error')
        return
      }
      setState(prev => ({ ...prev, apiKey: key }))
      addOutput('API key configured', 'success')
    },
    
    header: (header: string) => {
      if (!header) {
        addOutput('Usage: header <auth-header>', 'error')
        addOutput('Example: header Bearer your_token_here', 'info')
        return
      }
      setState(prev => ({ ...prev, authHeader: header }))
      addOutput('Authorization header configured', 'success')
    },
    
    status: () => {
      addOutput('━━━ SYSTEM STATUS ━━━', 'info')
      addOutput(`Endpoint: ${state.currentEndpoint || 'Not set'}`, 'output')
      addOutput(`API Key: ${state.apiKey ? '***configured***' : 'Not set'}`, 'output')
      addOutput(`Auth Header: ${state.authHeader ? '***configured***' : 'Not set'}`, 'output')
      addOutput(`Commands Executed: ${state.commandCount}`, 'output')
      addOutput('━━━━━━━━━━━━━━━━━━━━━━━━━━', 'info')
    }
  }

  const executeApiCommand = async (command: string, args: string[]) => {
    if (!state.currentEndpoint) {
      addOutput('Error: No endpoint configured. Use "endpoint <url>" first.', 'error')
      return
    }

    setState(prev => ({ ...prev, isExecuting: true }))
    addOutput('⚡ Executing command...', 'info')

    try {
      const result = await executeCommand(command, {
        endpoint: {
          url: state.currentEndpoint,
          api_key: state.apiKey || undefined,
          auth_header: state.authHeader || undefined
        },
        args
      })

      if (result.success && result.data) {
        addOutput('✅ Command executed successfully', 'success')
        addOutput(`⏱️  Execution time: ${result.execution_time?.toFixed(2)}s`, 'info')
        addOutput('━━━ RESULT ━━━', 'info')
        addOutput(JSON.stringify(result.data, null, 2), 'output')
      } else {
        addOutput(`❌ Command failed: ${result.error}`, 'error')
      }
    } catch (error) {
      addOutput(`💥 Network error: ${error}`, 'error')
    } finally {
      setState(prev => ({ ...prev, isExecuting: false }))
    }
  }

  const handleCommand = async (input: string) => {
    const trimmed = input.trim()
    if (!trimmed) return

    // Add to history
    setState(prev => ({
      ...prev,
      commandHistory: [...prev.commandHistory, trimmed],
      historyIndex: -1,
      commandCount: prev.commandCount + 1
    }))

    // Display command
    addOutput(`user@mcpeek:~$ ${trimmed}`, 'command')

    // Parse command
    const parts = trimmed.split(/\s+/)
    const cmd = parts[0].toLowerCase()
    const args = parts.slice(1)

    // Handle local commands
    if (cmd in commands) {
      (commands as any)[cmd](...args)
      return
    }

    // Handle MCP API commands
    switch (cmd) {
      case 'discover':
        await executeApiCommand('discover', args)
        break
      case 'tool':
        if (args.length < 1) {
          addOutput('Usage: tool <name> [json-params]', 'error')
          addOutput('Example: tool list_files {"path": "/"}', 'info')
          return
        }
        await executeApiCommand('tool', args)
        break
      case 'resource':
        if (args.length < 1) {
          addOutput('Usage: resource <uri>', 'error')
          addOutput('Example: resource file:///path/to/file.txt', 'info')
          return
        }
        await executeApiCommand('resource', args)
        break
      case 'prompt':
        if (args.length < 1) {
          addOutput('Usage: prompt <name> [json-params]', 'error')
          addOutput('Example: prompt summarize {"text": "content to summarize"}', 'info')
          return
        }
        await executeApiCommand('prompt', args)
        break
      default:
        addOutput(`Unknown command: ${cmd}`, 'error')
        addOutput('Type "help" to see available commands', 'info')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (state.isExecuting) return

    switch (e.key) {
      case 'Enter':
        if (state.currentInput.trim()) {
          handleCommand(state.currentInput)
          setState(prev => ({ ...prev, currentInput: '' }))
        }
        break
      
      case 'ArrowUp':
        e.preventDefault()
        if (state.commandHistory.length > 0) {
          const newIndex = state.historyIndex === -1 
            ? state.commandHistory.length - 1 
            : Math.max(0, state.historyIndex - 1)
          setState(prev => ({
            ...prev,
            historyIndex: newIndex,
            currentInput: prev.commandHistory[newIndex] || ''
          }))
        }
        break
      
      case 'ArrowDown':
        e.preventDefault()
        if (state.historyIndex !== -1) {
          const newIndex = state.historyIndex + 1
          if (newIndex >= state.commandHistory.length) {
            setState(prev => ({ ...prev, historyIndex: -1, currentInput: '' }))
          } else {
            setState(prev => ({
              ...prev,
              historyIndex: newIndex,
              currentInput: prev.commandHistory[newIndex]
            }))
          }
        }
        break
      
      case 'Tab':
        e.preventDefault()
        // Simple auto-complete
        const input = state.currentInput.toLowerCase()
        const availableCommands = ['help', 'clear', 'endpoint', 'auth', 'header', 'status', 'discover', 'tool', 'resource', 'prompt']
        const matches = availableCommands.filter(cmd => cmd.startsWith(input))
        if (matches.length === 1) {
          setState(prev => ({ ...prev, currentInput: matches[0] + ' ' }))
        } else if (matches.length > 1) {
          addOutput(`Available: ${matches.join(', ')}`, 'info')
        }
        break
    }
  }

  return (
    <TerminalContainer>
      <TerminalContent ref={contentRef}>
        {state.output.map(line => (
          <OutputLine key={line.id} type={line.type} className="slide-in">
            {line.content}
          </OutputLine>
        ))}
        
        <InputContainer>
          <Prompt>user@mcpeek:~$</Prompt>
          <Input
            ref={inputRef}
            value={state.currentInput}
            onChange={(e) => setState(prev => ({ ...prev, currentInput: e.target.value }))}
            onKeyDown={handleKeyDown}
            placeholder={state.isExecuting ? "Executing..." : "Enter command (try 'help')"}
            disabled={state.isExecuting}
          />
        </InputContainer>
      </TerminalContent>

      <HelpPanel visible={state.showHelp}>
        <HelpTitle>🎯 AVAILABLE COMMANDS</HelpTitle>
        <HelpCommand>
          <span className="command">help</span>
          <span className="description">Toggle this panel</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">clear</span>
          <span className="description">Clear terminal</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">endpoint &lt;url&gt;</span>
          <span className="description">Set MCP endpoint</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">auth &lt;key&gt;</span>
          <span className="description">Set API key</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">header &lt;auth&gt;</span>
          <span className="description">Set auth header</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">status</span>
          <span className="description">Show current settings</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">discover [-v]</span>
          <span className="description">Explore capabilities</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">tool &lt;name&gt; [params]</span>
          <span className="description">Execute MCP tool</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">resource &lt;uri&gt;</span>
          <span className="description">Read MCP resource</span>
        </HelpCommand>
        <HelpCommand>
          <span className="command">prompt &lt;name&gt; [args]</span>
          <span className="description">Get MCP prompt</span>
        </HelpCommand>
      </HelpPanel>

      <StatusBar
        currentEndpoint={state.currentEndpoint}
        connectionStatus={!!state.currentEndpoint}
        lastCommand={state.commandHistory[state.commandHistory.length - 1]}
        commandCount={state.commandCount}
      />
    </TerminalContainer>
  )
}

export default Terminal