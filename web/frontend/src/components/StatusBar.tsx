import React from 'react'
import styled from 'styled-components'

const StatusContainer = styled.div`
  background: rgba(0, 0, 0, 0.9);
  border-top: 1px solid #00ff00;
  padding: 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #00cc00;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 10;
  min-height: 32px;
`

const StatusLeft = styled.div`
  display: flex;
  gap: 20px;
  align-items: center;
`

const StatusRight = styled.div`
  display: flex;
  gap: 15px;
  align-items: center;
`

const StatusItem = styled.div<{ status?: 'active' | 'inactive' | 'warning' }>`
  display: flex;
  align-items: center;
  gap: 5px;
  
  &:before {
    content: '●';
    font-size: 8px;
    color: ${props => {
      switch (props.status) {
        case 'active': return '#00ff00'
        case 'warning': return '#ffff00'
        case 'inactive': return '#666666'
        default: return '#00cc00'
      }
    }};
    animation: ${props => props.status === 'active' ? 'pulse 1.5s ease-in-out infinite' : 'none'};
  }
`

const ConnectionStatus = styled.div<{ connected: boolean }>`
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  color: ${props => props.connected ? '#00ff00' : '#ff0000'};
  
  &:before {
    content: '📡';
    font-size: 10px;
  }
`

interface StatusBarProps {
  currentEndpoint?: string
  connectionStatus: boolean
  lastCommand?: string
  commandCount: number
}

const StatusBar: React.FC<StatusBarProps> = ({
  currentEndpoint,
  connectionStatus,
  lastCommand,
  commandCount
}) => {
  const [uptime, setUptime] = React.useState(0)

  React.useEffect(() => {
    const startTime = Date.now()
    const interval = setInterval(() => {
      setUptime(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const formatEndpoint = (endpoint?: string) => {
    if (!endpoint) return 'No endpoint set'
    try {
      const url = new URL(endpoint)
      return `${url.hostname}:${url.port || (url.protocol === 'https:' ? '443' : '80')}`
    } catch {
      return endpoint.length > 30 ? `${endpoint.substring(0, 30)}...` : endpoint
    }
  }

  return (
    <StatusContainer>
      <StatusLeft>
        <ConnectionStatus connected={connectionStatus}>
          {connectionStatus ? 'CONNECTED' : 'DISCONNECTED'}
        </ConnectionStatus>
        
        <StatusItem>
          ENDPOINT: {formatEndpoint(currentEndpoint)}
        </StatusItem>
        
        {lastCommand && (
          <StatusItem>
            LAST: {lastCommand}
          </StatusItem>
        )}
      </StatusLeft>
      
      <StatusRight>
        <StatusItem status="active">
          COMMANDS: {commandCount}
        </StatusItem>
        
        <StatusItem status="active">
          UPTIME: {formatUptime(uptime)}
        </StatusItem>
        
        <StatusItem status="active">
          CPU: {Math.floor(Math.random() * 15 + 10)}%
        </StatusItem>
        
        <StatusItem status="active">
          MEM: {Math.floor(Math.random() * 30 + 40)}%
        </StatusItem>
      </StatusRight>
    </StatusContainer>
  )
}

export default StatusBar