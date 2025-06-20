import React, { useState, useEffect, useRef } from 'react';
import styled, { createGlobalStyle, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import Terminal from './components/Terminal';
import MatrixRain from './components/MatrixRain';
import StatusBar from './components/StatusBar';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: 'Fira Code', 'JetBrains Mono', monospace;
    background-color: #000000;
    color: #00ff00;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }
  
  #root {
    height: 100vh;
    width: 100vw;
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

const AppContainer = styled.div`
  height: 100vh;
  width: 100vw;
  background-color: #000000;
  position: relative;
  display: flex;
  flex-direction: column;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      linear-gradient(90deg, transparent 98%, #00ff0015 100%),
      linear-gradient(0deg, transparent 98%, #00ff0015 100%);
    background-size: 3px 3px;
    pointer-events: none;
    z-index: 1;
  }
`;

const Header = styled(motion.header)`
  background: linear-gradient(90deg, #000000, #001100, #000000);
  border-bottom: 2px solid #00ff00;
  padding: 1rem;
  position: relative;
  z-index: 100;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, #00ff0008, transparent);
    animation: ${glitch} 2s infinite;
  }
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 
    0 0 10px #00ff00,
    0 0 20px #00ff00,
    0 0 30px #00ff00;
  animation: ${glitch} 3s infinite;
  
  span {
    color: #ffffff;
  }
`;

const Subtitle = styled.p`
  font-size: 1rem;
  margin-top: 0.5rem;
  opacity: 0.8;
  color: #00cc00;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  position: relative;
  overflow: hidden;
`;

const TerminalContainer = styled.div`
  flex: 1;
  position: relative;
  z-index: 10;
`;

const LoadingScreen = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #000000;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const LoadingText = styled.div`
  font-size: 1.5rem;
  color: #00ff00;
  margin-bottom: 2rem;
  text-shadow: 0 0 10px #00ff00;
`;

const LoadingBar = styled.div`
  width: 300px;
  height: 4px;
  background: #001100;
  border: 1px solid #00ff00;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, #00ff00, transparent);
    animation: loading 2s infinite;
  }
  
  @keyframes loading {
    0% { left: -100%; }
    100% { left: 100%; }
  }
`;

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [showMatrix, setShowMatrix] = useState(true);
  
  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 3000);
    
    return () => clearTimeout(timer);
  }, []);
  
  return (
    <>
      <GlobalStyle />
      <AppContainer>
        <AnimatePresence>
          {isLoading && (
            <LoadingScreen
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5 }}
            >
              <LoadingText>
                INITIALIZING MCPeek v1.0.0
              </LoadingText>
              <LoadingBar />
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                style={{ marginTop: '2rem', color: '#00cc00', fontSize: '0.9rem' }}
              >
                [LOADING] Establishing secure connection...
              </motion.div>
            </LoadingScreen>
          )}
        </AnimatePresence>
        
        {!isLoading && (
          <>
            <MatrixRain show={showMatrix} />
            
            <Header
              initial={{ y: -100 }}
              animate={{ y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Title>
                MCP<span>eek</span>
              </Title>
              <Subtitle>
                Model Context Protocol Explorer | v1.0.0 | AUTHENTICATED
              </Subtitle>
            </Header>
            
            <MainContent>
              <TerminalContainer>
                <Terminal />
              </TerminalContainer>
            </MainContent>
            
            <StatusBar />
          </>
        )}
      </AppContainer>
    </>
  );
}

export default App;