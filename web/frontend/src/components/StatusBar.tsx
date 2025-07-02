import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import { Activity, Wifi, Clock, Terminal } from 'lucide-react'

const StatusContainer = styled.div`
  background: rgba(0, 17, 0, 0.9);
  border-top: 1px solid #00ff00;
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
  color: #00ff00;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(5px);
`

const StatusGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`

const StatusItem = styled.div<{ $status?: 'online' | 'offline' | 'error' | 'connecting' }>`
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  
  ${({ $status }) => {
    switch ($status) {
      case 'online':
        return `
          color: #00ff00;
          text-shadow: 0 0 3px #00ff00;
        `
      case 'connecting':
        return `
          color: #ffaa00;
          text-shadow: 0 0 3px #ffaa00;
          animation: pulse 2s infinite;
        `
      case 'error':
        return `
          color: #ff0000;
          text-shadow: 0 0 3px #ff0000;
        `
      case 'offline':
      default:
        return `
          color: #666666;
        `
    }
  }}
  
  svg {
    width: 14px;
    height: 14px;
  }
`

const LiveClock = styled.div`
  font-family: 'Fira Code', monospace;
  font-weight: 600;
  color: #00ff00;
  text-shadow: 0 0 5px #00ff00;
  letter-spacing: 1px;
`

const UptimeCounter = styled.div`
  color: #00aa00;
  font-size: 11px;
`

const EndpointStatus = styled.div<{ $truncate?: boolean }>`
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #00cc00;
  font-size: 11px;
  
  ${({ $truncate }) => $truncate && `
    &:hover {
      overflow: visible;
      white-space: normal;
      word-break: break-all;
      position: absolute;
      background: rgba(0, 0, 0, 0.9);
      padding: 4px 8px;
      border: 1px solid #00ff00;
      border-radius: 4px;
      z-index: 1000;
      max-width: 400px;
    }
  `}
`

const ScanLine = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ff00, transparent);
  animation: scan 3s linear infinite;
  opacity: 0.3;
  
  @keyframes scan {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
`

interface StatusBarProps {
  endpoint: string | null
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error'
  uptime: number
  activeConnections: number
  lastCommand: string | null
}

const StatusBar: React.FC<StatusBarProps> = ({
  endpoint,
  connectionStatus,
  uptime,
  activeConnections,
  lastCommand
}) => {
  const [currentTime, setCurrentTime] = useState(new Date())
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    
    return () => clearInterval(timer)
  }, [])
  
  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }
  
  const getConnectionStatusText = (status: typeof connectionStatus): string => {
    switch (status) {
      case 'connected':
        return 'ONLINE'
      case 'connecting':
        return 'CONNECTING...'
      case 'error':
        return 'ERROR'
      case 'disconnected':
      default:
        return 'OFFLINE'
    }
  }
  
  const getConnectionIcon = (status: typeof connectionStatus) => {
    switch (status) {
      case 'connected':
        return <Wifi />
      case 'connecting':
        return <Activity className="pulse" />
      case 'error':
        return <Wifi />
      case 'disconnected':
      default:
        return <Wifi />
    }
  }
  
  return (
    <StatusContainer>
      <ScanLine />
      
      <StatusGroup>
        <StatusItem $status={connectionStatus === 'connected' ? 'online' : connectionStatus}>
          {getConnectionIcon(connectionStatus)}
          {getConnectionStatusText(connectionStatus)}
        </StatusItem>
        
        {endpoint && (
          <EndpointStatus $truncate title={endpoint}>
            TARGET: {endpoint}
          </EndpointStatus>
        )}
        
        <StatusItem>
          <Activity />
          CONN: {activeConnections}
        </StatusItem>
      </StatusGroup>
      
      <StatusGroup>
        {lastCommand && (
          <StatusItem>
            <Terminal />
            LAST: {lastCommand.length > 20 ? lastCommand.substring(0, 20) + '...' : lastCommand}
          </StatusItem>
        )}
        
        <UptimeCounter>
          <Clock style={{ width: 12, height: 12, marginRight: 4 }} />
          UP: {formatUptime(uptime)}
        </UptimeCounter>
        
        <LiveClock>
          {currentTime.toLocaleTimeString([], { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
          })}
        </LiveClock>
      </StatusGroup>
    </StatusContainer>
  )
}

export default StatusBar