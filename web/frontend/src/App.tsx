import React from 'react'
import styled from 'styled-components'
import Terminal from './components/Terminal'
import MatrixRain from './components/MatrixRain'
import StatusBar from './components/StatusBar'
import Header from './components/Header'

const AppContainer = styled.div`
  height: 100vh;
  width: 100vw;
  background: #000000;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 2;
`

const App: React.FC = () => {
  return (
    <AppContainer>
      <MatrixRain />
      <MainContent>
        <Header />
        <Terminal />
        <StatusBar />
      </MainContent>
    </AppContainer>
  )
}

export default App