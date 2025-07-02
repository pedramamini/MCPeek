import React from 'react'
import './App.css'

function App() {
  return (
    <div className="App">
      <div className="terminal">
        <div className="terminal-header">
          <div className="terminal-title glow">MCPeek v1.0.0 - Hacker Terminal</div>
          <div className="terminal-controls">
            <div className="control-btn close"></div>
            <div className="control-btn minimize"></div>
            <div className="control-btn maximize"></div>
          </div>
        </div>
        
        <div className="terminal-body">
          <div className="ascii-banner success">
            <pre>{`
███╗   ███╗ ██████╗██████╗ ███████╗███████╗██╗  ██╗
████╗ ████║██╔════╝██╔══██╗██╔════╝██╔════╝██║ ██╔╝
██╔████╔██║██║     ██████╔╝█████╗  █████╗  █████╔╝ 
██║╚██╔╝██║██║     ██╔═══╝ ██╔══╝  ██╔══╝  ██╔═██╗ 
██║ ╚═╝ ██║╚██████╗██║     ███████╗███████╗██║  ██╗
╚═╝     ╚═╝ ╚═════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝
            `}</pre>
          </div>
          
          <div className="welcome-message info">
            <p>Welcome to MCPeek Web Interface - The Ultimate MCP Exploration Terminal</p>
            <p>This is a simplified frontend build. The full interface is served by the backend.</p>
            <p><span className="warning">⚡ Navigate to the backend URL for the complete interface ⚡</span></p>
          </div>
        </div>
        
        <div className="status-bar">
          <span>Frontend Build Complete</span>
          <span id="time">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  )
}

export default App