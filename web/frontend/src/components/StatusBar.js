import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const pulse = keyframes`
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
`;

const StatusBarContainer = styled(motion.div)`
  background: linear-gradient(90deg, #000000, #001100, #000000);
  border-top: 1px solid #00ff00;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  font-family: 'Fira Code', monospace;
  position: relative;
  z-index: 100;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, #00ff0005, transparent);
  }
`;

const StatusSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #00cc00;
  
  .label {
    color: #ffffff;
  }
  
  .value {
    color: #00ff00;
    font-weight: 600;
  }
  
  &.online .indicator {
    background: #00ff00;
    animation: ${pulse} 2s infinite;
  }
  
  &.offline .indicator {
    background: #ff0040;
  }
`;

const Indicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 5px currentColor;
`;

const Clock = styled.div`
  color: #00ff00;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
`;

const SystemStats = styled.div`
  display: flex;
  gap: 1rem;
  font-size: 0.7rem;
`;

const StatusBar = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [connectionStatus, setConnectionStatus] = useState('online');
  const [serverInfo, setServerInfo] = useState({
    version: '1.0.0',
    uptime: '0d 0h 0m'
  });
  
  useEffect(() => {
    // Update clock every second
    const clockInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    // Check server health
    const healthCheck = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          setConnectionStatus('online');
        } else {
          setConnectionStatus('offline');
        }
      } catch (error) {
        setConnectionStatus('offline');
      }
    };
    
    // Initial health check
    healthCheck();
    
    // Check health every 30 seconds
    const healthInterval = setInterval(healthCheck, 30000);
    
    return () => {
      clearInterval(clockInterval);
      clearInterval(healthInterval);
    };
  }, []);
  
  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };
  
  return (
    <StatusBarContainer
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <StatusSection>
        <StatusItem className={connectionStatus}>
          <Indicator className="indicator" />
          <span className="label">STATUS:</span>
          <span className="value">{connectionStatus.toUpperCase()}</span>
        </StatusItem>
        
        <StatusItem>
          <span className="label">VER:</span>
          <span className="value">{serverInfo.version}</span>
        </StatusItem>
        
        <StatusItem>
          <span className="label">MODE:</span>
          <span className="value">SECURE</span>
        </StatusItem>
      </StatusSection>
      
      <StatusSection>
        <SystemStats>
          <div>
            <span style={{ color: '#ffffff' }}>CPU: </span>
            <span style={{ color: '#00ff00' }}>LOW</span>
          </div>
          <div>
            <span style={{ color: '#ffffff' }}>MEM: </span>
            <span style={{ color: '#00ff00' }}>OK</span>
          </div>
          <div>
            <span style={{ color: '#ffffff' }}>NET: </span>
            <span style={{ color: connectionStatus === 'online' ? '#00ff00' : '#ff0040' }}>
              {connectionStatus === 'online' ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
        </SystemStats>
      </StatusSection>
      
      <StatusSection>
        <div style={{ color: '#00cc00', fontSize: '0.7rem' }}>
          {formatDate(currentTime)}
        </div>
        <Clock>
          {formatTime(currentTime)}
        </Clock>
      </StatusSection>
    </StatusBarContainer>
  );
};

export default StatusBar;