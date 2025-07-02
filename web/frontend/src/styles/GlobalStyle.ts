import { createGlobalStyle } from 'styled-components'

export const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Fira Code', 'JetBrains Mono', monospace;
    background: #000000;
    color: #00ff00;
    overflow: hidden;
    height: 100vh;
    width: 100vw;
  }

  #root {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: #000000;
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb {
    background: #00ff00;
    border-radius: 4px;
    border: 1px solid #000000;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #00cc00;
  }

  ::-webkit-scrollbar-corner {
    background: #000000;
  }

  /* Text selection */
  ::selection {
    background: #00ff00;
    color: #000000;
  }

  ::-moz-selection {
    background: #00ff00;
    color: #000000;
  }

  /* Input styles */
  input, textarea, select {
    font-family: 'Fira Code', 'JetBrains Mono', monospace;
    background: #000000;
    color: #00ff00;
    border: 1px solid #00ff00;
    outline: none;
  }

  input:focus, textarea:focus, select:focus {
    border-color: #00cc00;
    box-shadow: 0 0 5px #00ff00;
  }

  /* Animation keyframes */
  @keyframes glow {
    0%, 100% { 
      text-shadow: 0 0 5px #00ff00; 
    }
    50% { 
      text-shadow: 0 0 10px #00ff00, 0 0 15px #00ff00; 
    }
  }

  @keyframes pulse {
    0%, 100% { 
      opacity: 1; 
    }
    50% { 
      opacity: 0.7; 
    }
  }

  @keyframes slideIn {
    from {
      transform: translateY(-10px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes matrix-drop {
    0% {
      transform: translateY(-100vh);
      opacity: 1;
    }
    100% {
      transform: translateY(100vh);
      opacity: 0;
    }
  }

  /* Utility classes */
  .glow {
    animation: glow 2s ease-in-out infinite;
  }

  .pulse {
    animation: pulse 1.5s ease-in-out infinite;
  }

  .slide-in {
    animation: slideIn 0.3s ease-out;
  }

  .text-shadow {
    text-shadow: 0 0 5px #00ff00;
  }

  .no-select {
    user-select: none;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
  }
`