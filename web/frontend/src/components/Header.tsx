import React from 'react'
import styled from 'styled-components'

const HeaderContainer = styled.header`
  background: rgba(0, 0, 0, 0.9);
  border-bottom: 1px solid #00ff00;
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 10;
`

const Logo = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    text-shadow: 0 0 15px #00ff00, 0 0 25px #00ff00;
    transform: scale(1.02);
  }

  &:before {
    content: '⚡';
    font-size: 28px;
    animation: pulse 2s ease-in-out infinite;
  }
`

const Title = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
`

const MainTitle = styled.div`
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 2px;
`

const SubTitle = styled.div`
  font-size: 12px;
  color: #00cc00;
  font-weight: 300;
  margin-top: -2px;
  letter-spacing: 3px;
  text-transform: uppercase;
`

const SystemInfo = styled.div`
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #00cc00;
  font-weight: 400;
`

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  
  &:before {
    content: '●';
    color: #00ff00;
    animation: pulse 1.5s ease-in-out infinite;
  }
`

const Header: React.FC = () => {
  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const [currentTime, setCurrentTime] = React.useState(getCurrentTime())

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(getCurrentTime())
    }, 1000)

    return () => clearInterval(interval)
  }, [])

  return (
    <HeaderContainer>
      <Logo>
        <Title>
          <MainTitle>MCPeek</MainTitle>
          <SubTitle>Hacker Terminal</SubTitle>
        </Title>
      </Logo>
      
      <SystemInfo>
        <InfoItem>SYSTEM: ACTIVE</InfoItem>
        <InfoItem>TIME: {currentTime}</InfoItem>
        <InfoItem>STATUS: READY</InfoItem>
      </SystemInfo>
    </HeaderContainer>
  )
}

export default Header