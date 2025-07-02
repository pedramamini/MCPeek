import React from 'react'
import styled from 'styled-components'
import { X, Terminal, Zap, Database, MessageSquare, Key, Settings, Info } from 'lucide-react'

const HelpContainer = styled.div`
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  border-left: 1px solid #00ff00;
  display: flex;
  flex-direction: column;
  position: relative;
  backdrop-filter: blur(10px);
`

const HelpHeader = styled.div`
  background: rgba(0, 255, 0, 0.1);
  border-bottom: 1px solid #00ff00;
  padding: 12px 16px;
  display: flex;
  justify-content: between;
  align-items: center;
  font-family: 'Fira Code', monospace;
  font-weight: 600;
  color: #00ff00;
  text-shadow: 0 0 5px #00ff00;
`

const HelpTitle = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  
  svg {
    width: 16px;
    height: 16px;
  }
`

const CloseButton = styled.button`
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 10px #00ff0050;
  }
  
  svg {
    width: 14px;
    height: 14px;
  }
`

const HelpContent = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.5;
`

const Section = styled.div`
  margin-bottom: 24px;
`

const SectionTitle = styled.h3`
  color: #00ff00;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  text-shadow: 0 0 5px #00ff00;
  
  svg {
    width: 16px;
    height: 16px;
  }
`

const CommandList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const Command = styled.div`
  background: rgba(0, 17, 0, 0.3);
  border: 1px solid #00aa00;
  border-radius: 4px;
  padding: 8px 12px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #00ff00;
    box-shadow: 0 0 5px #00ff0030;
  }
`

const CommandSyntax = styled.div`
  color: #00ff00;
  font-weight: 600;
  margin-bottom: 4px;
`

const CommandDescription = styled.div`
  color: #00cc00;
  font-size: 11px;
`

const Example = styled.div`
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #006600;
  border-radius: 4px;
  padding: 8px;
  margin-top: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 11px;
  color: #00aa00;
`

const KeyboardShortcuts = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 8px;
  margin-top: 8px;
`

const Shortcut = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  background: rgba(0, 17, 0, 0.3);
  border-radius: 4px;
  font-size: 11px;
`

const ShortcutKey = styled.kbd`
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid #00ff00;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 10px;
  color: #00ff00;
  text-shadow: 0 0 3px #00ff00;
`

const ShortcutDesc = styled.span`
  color: #00cc00;
`

interface HelpPanelProps {
  onClose: () => void
}

const HelpPanel: React.FC<HelpPanelProps> = ({ onClose }) => {
  const commands = [
    {
      syntax: 'endpoint <url>',
      description: 'Set the MCP endpoint URL to connect to',
      example: 'endpoint http://localhost:8000/mcp'
    },
    {
      syntax: 'discover [-v|-vv|-vvv]',
      description: 'Explore endpoint capabilities with optional verbosity levels',
      example: 'discover -vv'
    },
    {
      syntax: 'tool <name> [params]',
      description: 'Execute a specific MCP tool with optional JSON parameters',
      example: 'tool search {"query": "hello world"}'
    },
    {
      syntax: 'resource <uri>',
      description: 'Read a specific MCP resource',
      example: 'resource file://path/to/file.txt'
    },
    {
      syntax: 'prompt <name> [args]',
      description: 'Get a specific MCP prompt with optional JSON arguments',
      example: 'prompt summarize {"text": "Long text to summarize"}'
    },
    {
      syntax: 'auth <api-key>',
      description: 'Set API key for authentication',
      example: 'auth your-secret-api-key'
    },
    {
      syntax: 'header <auth-header>',
      description: 'Set custom authorization header',
      example: 'header Bearer your-token'
    },
    {
      syntax: 'status',
      description: 'Show current connection and authentication status',
      example: 'status'
    },
    {
      syntax: 'clear',
      description: 'Clear the terminal output',
      example: 'clear'
    },
    {
      syntax: 'help',
      description: 'Toggle this help panel',
      example: 'help'
    }
  ]
  
  const shortcuts = [
    { key: '↑/↓', desc: 'Command history' },
    { key: 'Tab', desc: 'Auto-complete' },
    { key: 'Enter', desc: 'Execute command' },
    { key: 'Ctrl+C', desc: 'Cancel operation' },
    { key: 'Ctrl+L', desc: 'Clear terminal' },
    { key: 'Esc', desc: 'Close help panel' }
  ]
  
  return (
    <HelpContainer>
      <HelpHeader>
        <HelpTitle>
          <Info />
          HACKER TERMINAL HELP
        </HelpTitle>
        <CloseButton onClick={onClose}>
          <X />
        </CloseButton>
      </HelpHeader>
      
      <HelpContent>
        <Section>
          <SectionTitle>
            <Terminal />
            Available Commands
          </SectionTitle>
          <CommandList>
            {commands.map((cmd, index) => (
              <Command key={index}>
                <CommandSyntax>{cmd.syntax}</CommandSyntax>
                <CommandDescription>{cmd.description}</CommandDescription>
                <Example>$ {cmd.example}</Example>
              </Command>
            ))}
          </CommandList>
        </Section>
        
        <Section>
          <SectionTitle>
            <Zap />
            Quick Start
          </SectionTitle>
          <Command>
            <CommandDescription>
              1. Set an endpoint: <code>endpoint http://localhost:8000/mcp</code><br/>
              2. Discover capabilities: <code>discover -v</code><br/>
              3. Execute tools: <code>tool search {"{\"query\": \"test\"}"}</code><br/>
              4. Read resources: <code>resource file://example.txt</code>
            </CommandDescription>
          </Command>
        </Section>
        
        <Section>
          <SectionTitle>
            <Key />
            Keyboard Shortcuts  
          </SectionTitle>
          <KeyboardShortcuts>
            {shortcuts.map((shortcut, index) => (
              <Shortcut key={index}>
                <ShortcutKey>{shortcut.key}</ShortcutKey>
                <ShortcutDesc>{shortcut.desc}</ShortcutDesc>
              </Shortcut>
            ))}
          </KeyboardShortcuts>
        </Section>
        
        <Section>
          <SectionTitle>
            <Database />
            MCP Protocol
          </SectionTitle>
          <Command>
            <CommandDescription>
              Model Context Protocol (MCP) allows AI applications to connect to external data sources and tools. 
              This interface provides a hacker-themed terminal for exploring MCP endpoints, executing tools, 
              reading resources, and working with prompts.
            </CommandDescription>
          </Command>
        </Section>
        
        <Section>
          <SectionTitle>
            <Settings />
            Authentication
          </SectionTitle>
          <Command>
            <CommandDescription>
              • Use <code>auth</code> command to set API keys<br/>
              • Use <code>header</code> command for custom auth headers<br/>
              • Authentication is persistent within the session<br/>
              • Check <code>status</code> to verify current auth settings
            </CommandDescription>
          </Command>
        </Section>
        
        <Section>
          <SectionTitle>
            <MessageSquare />
            Tips & Tricks
          </SectionTitle>
          <Command>
            <CommandDescription>
              • Use <code>-v</code>, <code>-vv</code>, or <code>-vvv</code> for increased verbosity<br/>
              • JSON parameters must be valid JSON format<br/>
              • Tab completion works for command names<br/>
              • Arrow keys navigate command history<br/>
              • Terminal supports full copy/paste operations
            </CommandDescription>
          </Command>
        </Section>
      </HelpContent>
    </HelpContainer>
  )
}

export default HelpPanel