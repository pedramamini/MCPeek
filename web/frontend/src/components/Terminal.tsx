import React, { useState, useEffect, useRef, useCallback } from 'react'
import styled from 'styled-components'
import axios from 'axios'

const TerminalContainer = styled.div`
  flex: 1;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #00ff00;
  border-radius: 4px;
  margin: 60px 20px 0 20px;
  overflow: hidden;
  position: relative;
  box-shadow: 
    0 0 20px #00ff0030,
    inset 0 0 20px #00110020;
`

const TerminalHeader = styled.div`
  background: rgba(0, 255, 0, 0.1);
  border-bottom: 1px solid #00ff00;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
`

const WindowControls = styled.div`
  display: flex;
  gap: 8px;
`

const WindowControl = styled.div<{ color: string }>`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${({ color }) => color};
  box-shadow: 0 0 5px ${({ color }) => color};
  cursor: pointer;
  
  &:hover {
    box-shadow: 0 0 10px ${({ color }) => color};
  }
`

const TerminalTitle = styled.div`
  color: #00ff00;
  text-shadow: 0 0 5px #00ff00;
`

const TerminalBody = styled.div`
  height: calc(100% - 40px);
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.4;
`

const TerminalOutput = styled.div`
  flex: 1;
  margin-bottom: 16px;
`

const TerminalLine = styled.div<{ type?: 'input' | 'output' | 'error' | 'success' | 'info' | 'warning' }>`
  display: flex;
  align-items: flex-start;
  margin-bottom: 4px;
  word-break: break-all;
  
  ${({ type }) => {
    switch (type) {
      case 'error':
        return 'color: #ff0000; text-shadow: 0 0 5px #ff0000;'
      case 'success':
        return 'color: #00ff00; text-shadow: 0 0 5px #00ff00;'
      case 'info':
        return 'color: #00aaff; text-shadow: 0 0 5px #00aaff;'
      case 'warning':
        return 'color: #ffaa00; text-shadow: 0 0 5px #ffaa00;'
      case 'output':
        return 'color: #00cc00;'
      default:
        return 'color: #00ff00;'
    }
  }}
`

const Prompt = styled.span`
  color: #00ff00;
  font-weight: 600;
  text-shadow: 0 0 5px #00ff00;
  white-space: nowrap;
  margin-right: 8px;
  user-select: none;
`

const InputContainer = styled.div`
  display: flex;
  align-items: center;
  border-top: 1px solid #00ff0020;
  padding-top: 8px;
`

const TerminalInput = styled.input`
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
`

const JsonOutput = styled.pre`
  background: rgba(0, 17, 0, 0.5);
  border: 1px solid #00aa00;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
  overflow-x: auto;
  font-size: 12px;
  color: #00cc00;
  white-space: pre-wrap;
  word-break: break-word;
`

interface TerminalLine {
  id: string
  type: 'input' | 'output' | 'error' | 'success' | 'info' | 'warning'
  content: string
  timestamp: Date
}

interface TerminalProps {
  currentEndpoint: string | null
  apiKey: string | null
  authHeader: string | null
  onEndpointChange: (endpoint: string | null) => void
  onAuthChange: (apiKey: string | null, authHeader: string | null) => void
  onConnectionStatusChange: (status: 'disconnected' | 'connecting' | 'connected' | 'error') => void
  onHelpToggle: () => void
  onCommandExecuted: (command: string) => void
}

const Terminal: React.FC<TerminalProps> = ({
  currentEndpoint,
  apiKey,
  authHeader,
  onEndpointChange,
  onAuthChange,
  onConnectionStatusChange,
  onHelpToggle,
  onCommandExecuted
}) => {
  const [lines, setLines] = useState<TerminalLine[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [commandHistory, setCommandHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const [isLoading, setIsLoading] = useState(false)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  
  // Focus input on mount and click
  useEffect(() => {
    inputRef.current?.focus()
  }, [])
  
  // Scroll to bottom when new lines are added
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [lines])
  
  // Welcome message
  useEffect(() => {
    addLine('success', '🚀 MCPeek Hacker Terminal Interface Initialized')
    addLine('info', 'Type "help" to see available commands')
    addLine('info', 'Use "endpoint <url>" to connect to an MCP server')
  }, [])
  
  const addLine = useCallback((type: TerminalLine['type'], content: string) => {
    const line: TerminalLine = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      content,
      timestamp: new Date()
    }
    setLines(prev => [...prev, line])
  }, [])
  
  const formatJsonOutput = (data: any): string => {
    return JSON.stringify(data, null, 2)
  }
  
  const executeCommand = async (command: string) => {
    const trimmedCommand = command.trim()
    if (!trimmedCommand) return
    
    // Add command to history
    setCommandHistory(prev => [...prev, trimmedCommand])
    setHistoryIndex(-1)
    
    // Add input line
    addLine('input', `$ ${trimmedCommand}`)
    onCommandExecuted(trimmedCommand)
    
    const parts = trimmedCommand.split(' ')
    const cmd = parts[0].toLowerCase()
    const args = parts.slice(1)
    
    setIsLoading(true)
    onConnectionStatusChange('connecting')
    
    try {
      switch (cmd) {
        case 'help':
          onHelpToggle()
          addLine('info', 'Help panel toggled. Available commands:')
          addLine('output', 'endpoint <url> - Set MCP endpoint')
          addLine('output', 'discover [-v|-vv|-vvv] - Explore capabilities')
          addLine('output', 'tool <name> [params] - Execute tool')
          addLine('output', 'resource <uri> - Read resource')
          addLine('output', 'prompt <name> [args] - Get prompt')
          addLine('output', 'auth <api-key> - Set authentication')
          addLine('output', 'header <auth-header> - Set custom header')
          addLine('output', 'status - Show current settings')
          addLine('output', 'clear - Clear terminal')
          break
          
        case 'clear':
          setLines([])
          addLine('success', 'Terminal cleared')
          break
          
        case 'endpoint':
          if (args.length === 0) {
            addLine('error', 'Usage: endpoint <url>')
            break
          }
          const endpoint = args[0]
          onEndpointChange(endpoint)
          addLine('success', `Endpoint set to: ${endpoint}`)
          break
          
        case 'auth':
          if (args.length === 0) {
            addLine('error', 'Usage: auth <api-key>')
            break
          }
          const key = args.join(' ')
          onAuthChange(key, authHeader)
          addLine('success', 'API key updated')
          break
          
        case 'header':
          if (args.length === 0) {
            addLine('error', 'Usage: header <auth-header>')
            break
          }
          const header = args.join(' ')
          onAuthChange(apiKey, header)
          addLine('success', 'Auth header updated')
          break
          
        case 'status':
          addLine('info', '=== Current Status ===')
          addLine('output', `Endpoint: ${currentEndpoint || 'Not set'}`)
          addLine('output', `API Key: ${apiKey ? '***' + apiKey.slice(-4) : 'Not set'}`)
          addLine('output', `Auth Header: ${authHeader ? 'Set' : 'Not set'}`)
          break
          
        case 'discover':
          if (!currentEndpoint) {
            addLine('error', 'No endpoint set. Use: endpoint <url>')
            break
          }
          
          let verbosity = 1
          if (args.includes('-vv')) verbosity = 3
          else if (args.includes('-v')) verbosity = 2
          
          const discoverResponse = await axios.post('/api/discover', {
            url: currentEndpoint,
            verbosity,
            api_key: apiKey,
            auth_header: authHeader
          })
          
          addLine('success', 'Discovery completed:')
          addLine('output', formatJsonOutput(discoverResponse.data.data))
          break
          
        case 'tool':
          if (!currentEndpoint) {
            addLine('error', 'No endpoint set. Use: endpoint <url>')
            break
          }
          if (args.length === 0) {
            addLine('error', 'Usage: tool <name> [json-params]')
            break
          }
          
          const toolName = args[0]
          let toolParams = {}
          if (args.length > 1) {
            try {
              toolParams = JSON.parse(args.slice(1).join(' '))
            } catch (e) {
              addLine('error', 'Invalid JSON parameters')
              break
            }
          }
          
          const toolResponse = await axios.post('/api/tool', {
            url: currentEndpoint,
            tool_name: toolName,
            parameters: toolParams,
            api_key: apiKey,
            auth_header: authHeader
          })
          
          addLine('success', `Tool "${toolName}" executed:`)
          addLine('output', formatJsonOutput(toolResponse.data.data))
          break
          
        case 'resource':
          if (!currentEndpoint) {
            addLine('error', 'No endpoint set. Use: endpoint <url>')
            break
          }
          if (args.length === 0) {
            addLine('error', 'Usage: resource <uri>')
            break
          }
          
          const resourceUri = args[0]
          const resourceResponse = await axios.post('/api/resource', {
            url: currentEndpoint,
            resource_uri: resourceUri,
            api_key: apiKey,
            auth_header: authHeader
          })
          
          addLine('success', `Resource "${resourceUri}" read:`)
          addLine('output', formatJsonOutput(resourceResponse.data.data))
          break
          
        case 'prompt':
          if (!currentEndpoint) {
            addLine('error', 'No endpoint set. Use: endpoint <url>')
            break
          }
          if (args.length === 0) {
            addLine('error', 'Usage: prompt <name> [json-args]')
            break
          }
          
          const promptName = args[0]
          let promptArgs = {}
          if (args.length > 1) {
            try {
              promptArgs = JSON.parse(args.slice(1).join(' '))
            } catch (e) {
              addLine('error', 'Invalid JSON arguments')
              break
            }
          }
          
          const promptResponse = await axios.post('/api/prompt', {
            url: currentEndpoint,
            prompt_name: promptName,
            arguments: promptArgs,
            api_key: apiKey,
            auth_header: authHeader
          })
          
          addLine('success', `Prompt "${promptName}" retrieved:`)
          addLine('output', formatJsonOutput(promptResponse.data.data))
          break
          
        default:
          addLine('error', `Unknown command: ${cmd}. Type "help" for available commands.`)
      }
      
      onConnectionStatusChange('connected')
      
    } catch (error: any) {
      onConnectionStatusChange('error')
      addLine('error', `Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      executeCommand(currentInput)
      setCurrentInput('')
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (commandHistory.length > 0) {
        const newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1)
        setHistoryIndex(newIndex)
        setCurrentInput(commandHistory[newIndex])
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex >= 0) {
        const newIndex = historyIndex + 1
        if (newIndex >= commandHistory.length) {
          setHistoryIndex(-1)
          setCurrentInput('')
        } else {
          setHistoryIndex(newIndex)
          setCurrentInput(commandHistory[newIndex])
        }
      }
    } else if (e.key === 'Tab') {
      e.preventDefault()
      // Basic tab completion for commands
      const commands = ['help', 'clear', 'endpoint', 'discover', 'tool', 'resource', 'prompt', 'auth', 'header', 'status']
      const matches = commands.filter(cmd => cmd.startsWith(currentInput.toLowerCase()))
      if (matches.length === 1) {
        setCurrentInput(matches[0] + ' ')
      }
    }
  }
  
  const handleContainerClick = () => {
    inputRef.current?.focus()
  }
  
  return (
    <TerminalContainer onClick={handleContainerClick}>
      <TerminalHeader>
        <TerminalTitle>MCPeek Terminal v1.0.0 - {currentEndpoint || 'No endpoint'}</TerminalTitle>
        <WindowControls>
          <WindowControl color="#ff5f57" />
          <WindowControl color="#ffbd2e" />
          <WindowControl color="#28ca42" />
        </WindowControls>
      </TerminalHeader>
      
      <TerminalBody>
        <TerminalOutput ref={outputRef}>
          {lines.map(line => (
            <TerminalLine key={line.id} type={line.type}>
              {line.type === 'output' && line.content.startsWith('{') ? (
                <JsonOutput>{line.content}</JsonOutput>
              ) : (
                line.content
              )}
            </TerminalLine>
          ))}
          {isLoading && (
            <TerminalLine type="info">
              <span className="pulse">Executing command...</span>
            </TerminalLine>
          )}
        </TerminalOutput>
        
        <InputContainer>
          <Prompt>root@mcpeek:~$</Prompt>
          <TerminalInput
            ref={inputRef}
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command..."
            disabled={isLoading}
          />
          {!isLoading && <span className="terminal-cursor" />}
        </InputContainer>
      </TerminalBody>
    </TerminalContainer>
  )
}

export default Terminal