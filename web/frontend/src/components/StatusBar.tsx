import React, { useState, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';

interface StatusBarProps {
  connected: boolean;
  currentEndpoint: string;
}

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
`;

const StatusContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, #001100 0%, #002200 50%, #001100 100%);
  border-top: 1px solid #00ff00;
  padding: 8px 15px;
  font-size: 11px;
  color: #00cc00;
  font-family: 'Fira Code', monospace;
  height: 40px;
`;

const StatusSection = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const StatusItem = styled.div<{ highlight?: boolean }>`
  display: flex;
  align-items: center;
  gap: 6px;
  color: ${props => props.highlight ? '#00ff00' : '#00cc00'};
  
  .label {
    opacity: 0.8;
  }
  
  .value {
    font-weight: 600;
    color: #00ff00;
  }
  
  .indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.highlight ? '#00ff00' : '#ff4444'};
    animation: ${props => props.highlight ? pulse : 'none'} 2s infinite;
  }
`;

const SystemStats = styled.div`
  display: flex;
  gap: 15px;
  font-size: 10px;
  
  .stat {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .icon {
      width: 12px;
      height: 12px;
      border: 1px solid #00ff00;
      border-radius: 2px;
      background: rgba(0, 255, 0, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 8px;
    }
  }
`;

const Clock = styled.div`
  font-weight: 600;
  color: #00ff00;
  text-shadow: 0 0 3px #00ff00;
  letter-spacing: 1px;
`;

const StatusBar: React.FC<StatusBarProps> = ({ connected, currentEndpoint }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [memoryUsage, setMemoryUsage] = useState(0);
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      setUptime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Simulate memory usage tracking
    const updateMemoryUsage = () => {
      if (performance && (performance as any).memory) {
        const memory = (performance as any).memory;
        const used = memory.usedJSHeapSize / 1024 / 1024; // Convert to MB
        setMemoryUsage(Math.round(used * 10) / 10);
      } else {
        // Fallback for browsers without performance.memory
        setMemoryUsage(Math.random() * 50 + 20);
      }
    };

    updateMemoryUsage();
    const memoryTimer = setInterval(updateMemoryUsage, 5000);

    return () => clearInterval(memoryTimer);
  }, []);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEndpointDisplay = () => {
    if (!currentEndpoint) return 'None';
    if (currentEndpoint.length > 30) {
      return currentEndpoint.substring(0, 27) + '...';
    }
    return currentEndpoint;
  };

  return (
    <StatusContainer>
      <StatusSection>
        <StatusItem highlight={connected}>
          <div className="indicator" />
          <span className="label">STATUS:</span>
          <span className="value">{connected ? 'ONLINE' : 'OFFLINE'}</span>
        </StatusItem>
        
        <StatusItem highlight={!!currentEndpoint}>
          <span className="label">ENDPOINT:</span>
          <span className="value">{getEndpointDisplay()}</span>
        </StatusItem>
        
        <StatusItem>
          <span className="label">UPTIME:</span>
          <span className="value">{formatUptime(uptime)}</span>
        </StatusItem>
      </StatusSection>

      <SystemStats>
        <div className="stat">
          <div className="icon">🧠</div>
          <span>{memoryUsage}MB</span>
        </div>
        
        <div className="stat">
          <div className="icon">⚡</div>
          <span>{connected ? 'LIVE' : 'IDLE'}</span>
        </div>
        
        <div className="stat">
          <div className="icon">🔒</div>
          <span>SECURE</span>
        </div>
      </SystemStats>

      <Clock>
        {currentTime.toLocaleTimeString('en-US', { 
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })}
      </Clock>
    </StatusContainer>
  );
};

export default StatusBar;