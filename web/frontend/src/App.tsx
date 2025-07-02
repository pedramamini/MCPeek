import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import Terminal from './components/Terminal'
import MatrixRain from './components/MatrixRain'
import StatusBar from './components/StatusBar'
import HelpPanel from './components/HelpPanel'

const AppContainer = styled.div`
  position: relative;
  width: 100vw;
  height: 100vh;
  background: #000000;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`

const MainContent = styled.div`
  display: flex;
  flex: 1;
  position: relative;
  z-index: 2;
`

const TerminalContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
`

const SidePanel = styled.div<{ isOpen: boolean }>`
  width: ${({ isOpen }) => (isOpen ? '350px' : '0')};
  transition: width 0.3s ease;
  overflow: hidden;
  background: rgba(0, 17, 0, 0.8);
  border-left: ${({ isOpen }) => (isOpen ? '1px solid #00ff00' : 'none')};
  backdrop-filter: blur(5px);
`

const Logo = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  font-family: 'Fira Code', monospace;
  font-weight: 700;
  font-size: 24px;
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  
  &:hover {
    animation: glitch 0.5s ease-in-out;
    text-shadow: 0 0 20px #00ff00;
  }
  
  @keyframes glitch {
    0%, 100% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
  }
`

const SubTitle = styled.div`
  font-size: 10px;
  font-weight: 400;
  margin-top: 4px;
  color: #00aa00;
  text-shadow: 0 0 5px #00aa00;
  letter-spacing: 2px;
`

interface AppState {
  currentEndpoint: string | null
  apiKey: string | null
  authHeader: string | null
  isHelpOpen: boolean
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error'
  systemInfo: {
    uptime: number
    activeConnections: number
    lastCommand: string | null
  }
}

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    currentEndpoint: null,
    apiKey: null,
    authHeader: null,
    isHelpOpen: false,
    connectionStatus: 'disconnected',
    systemInfo: {
      uptime: 0,
      activeConnections: 0,
      lastCommand: null
    }
  })

  // Update uptime every second
  useEffect(() => {
    const startTime = Date.now()
    const interval = setInterval(() => {
      setState(prev => ({
        ...prev,
        systemInfo: {
          ...prev.systemInfo,
          uptime: Math.floor((Date.now() - startTime) / 1000)
        }
      }))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const updateEndpoint = (endpoint: string | null) => {
    setState(prev => ({ ...prev, currentEndpoint: endpoint }))
  }

  const updateAuth = (apiKey: string | null, authHeader: string | null) => {
    setState(prev => ({ ...prev, apiKey, authHeader }))
  }

  const updateConnectionStatus = (status: AppState['connectionStatus']) => {
    setState(prev => ({ ...prev, connectionStatus: status }))
  }

  const toggleHelp = () => {
    setState(prev => ({ ...prev, isHelpOpen: !prev.isHelpOpen }))
  }

  const updateLastCommand = (command: string) => {
    setState(prev => ({
      ...prev,
      systemInfo: {
        ...prev.systemInfo,
        lastCommand: command
      }
    }))
  }

  return (
    <AppContainer>
      {/* Matrix Rain Background */}
      <MatrixRain />
      
      {/* Logo */}
      <Logo onClick={() => window.location.reload()}>
        MCPeek
        <SubTitle>HACKER TERMINAL</SubTitle>
      </Logo>
      
      {/* Main Content */}
      <MainContent>
        <TerminalContainer>
          <Terminal
            currentEndpoint={state.currentEndpoint}
            apiKey={state.apiKey}
            authHeader={state.authHeader}
            onEndpointChange={updateEndpoint}
            onAuthChange={updateAuth}
            onConnectionStatusChange={updateConnectionStatus}
            onHelpToggle={toggleHelp}
            onCommandExecuted={updateLastCommand}
          />
          
          <StatusBar
            endpoint={state.currentEndpoint}
            connectionStatus={state.connectionStatus}
            uptime={state.systemInfo.uptime}
            activeConnections={state.systemInfo.activeConnections}
            lastCommand={state.systemInfo.lastCommand}
          />
        </TerminalContainer>
        
        <SidePanel isOpen={state.isHelpOpen}>
          <HelpPanel onClose={() => setState(prev => ({ ...prev, isHelpOpen: false }))} />
        </SidePanel>
      </MainContent>
    </AppContainer>
  )
}

export default App