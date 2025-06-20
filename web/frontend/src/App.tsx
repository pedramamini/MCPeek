import React, { useState, useEffect, useRef } from 'react';
import styled, { createGlobalStyle, keyframes } from 'styled-components';
import Terminal from './components/Terminal';
import StatusBar from './components/StatusBar';
import MatrixRain from './components/MatrixRain';

// Global styles with hacker aesthetic
const GlobalStyle = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap');
  
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: 'Fira Code', 'Cascadia Code', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
    background: #000000;
    color: #00ff00;
    overflow: hidden;
    font-size: 14px;
    line-height: 1.4;
  }
  
  ::-webkit-scrollbar {
    width: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: #000000;
  }
  
  ::-webkit-scrollbar-thumb {
    background: #00ff00;
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: #00cc00;
  }
  
  ::selection {
    background: #00ff0040;
  }
`;

const glitch = keyframes`
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
`;

const glow = keyframes`
  0%, 100% { 
    text-shadow: 
      0 0 5px #00ff00,
      0 0 10px #00ff00,
      0 0 15px #00ff00,
      0 0 20px #00ff00;
  }
  50% { 
    text-shadow: 
      0 0 2px #00ff00,
      0 0 5px #00ff00,
      0 0 8px #00ff00,
      0 0 12px #00ff00;
  }
`;

const AppContainer = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #000000;
  position: relative;
  overflow: hidden;
`;

const Header = styled.div`
  background: linear-gradient(90deg, #001100 0%, #003300 50%, #001100 100%);
  border-bottom: 2px solid #00ff00;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 255, 0, 0.3);
  z-index: 1000;
  position: relative;
`;

const Logo = styled.h1`
  font-size: 24px;
  font-weight: 700;
  color: #00ff00;
  text-shadow: 
    0 0 5px #00ff00,
    0 0 10px #00ff00,
    0 0 15px #00ff00;
  animation: ${glow} 2s ease-in-out infinite alternate;
  letter-spacing: 2px;
  
  &:hover {
    animation: ${glitch} 0.3s ease-in-out;
  }
`;

const SubTitle = styled.div`
  font-size: 12px;
  color: #00cc00;
  opacity: 0.8;
  letter-spacing: 1px;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
`;

const TerminalContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 10;
`;

const ConnectionStatus = styled.div<{ connected: boolean }>`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: ${props => props.connected ? '#00ff00' : '#ff4444'};
  
  &::before {
    content: '●';
    font-size: 16px;
    animation: ${props => props.connected ? glow : 'none'} 1s ease-in-out infinite alternate;
  }
`;

const WelcomeMessage = styled.div`
  color: #00aa00;
  font-size: 12px;
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid #004400;
  background: rgba(0, 20, 0, 0.8);
  
  .ascii-art {
    font-size: 10px;
    line-height: 1;
    margin: 10px 0;
    color: #00ff00;
    white-space: pre;
  }
`;

const App: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [currentEndpoint, setCurrentEndpoint] = useState<string>('');

  const asciiArt = `
    ███╗   ███╗ ██████╗██████╗ ███████╗███████╗██╗  ██╗
    ████╗ ████║██╔════╝██╔══██╗██╔════╝██╔════╝██║ ██╔╝
    ██╔████╔██║██║     ██████╔╝█████╗  █████╗  █████╔╝ 
    ██║╚██╔╝██║██║     ██╔═══╝ ██╔══╝  ██╔══╝  ██╔═██╗ 
    ██║ ╚═╝ ██║╚██████╗██║     ███████╗███████╗██║  ██╗
    ╚═╝     ╚═╝ ╚═════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝
                                                        
             [ MODEL CONTEXT PROTOCOL EXPLORER ]
    `;

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          setConnected(true);
        }
      } catch (error) {
        setConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <GlobalStyle />
      <AppContainer>
        {/* Matrix rain effect in background */}
        <MatrixRain />
        
        <Header>
          <div>
            <Logo>MCPeek</Logo>
            <SubTitle>TERMINAL INTERFACE v1.0</SubTitle>
          </div>
          <ConnectionStatus connected={connected}>
            {connected ? 'SYSTEM ONLINE' : 'CONNECTION LOST'}
          </ConnectionStatus>
        </Header>

        <WelcomeMessage>
          <div className="ascii-art">{asciiArt}</div>
          <div>
            Welcome to MCPeek Web Terminal - The most badass MCP exploration interface
            <br />
            Type 'help' to see available commands | Use arrow keys for history | Tab for completion
          </div>
        </WelcomeMessage>

        <MainContent>
          <TerminalContainer>
            <Terminal 
              onEndpointChange={setCurrentEndpoint}
              currentEndpoint={currentEndpoint}
            />
            <StatusBar 
              connected={connected}
              currentEndpoint={currentEndpoint}
            />
          </TerminalContainer>
        </MainContent>
      </AppContainer>
    </>
  );
};

export default App;