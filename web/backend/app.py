#!/usr/bin/env python3
"""
MCPeek Web Interface Backend
Badass hacker-themed REST API for MCP exploration
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Add the parent directory to the path to import mcpeek
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.mcpeek.config import Config
    from src.mcpeek.auth import AuthManager
    from src.mcpeek.mcp_client import MCPClient
    from src.mcpeek.discovery import DiscoveryEngine
    from src.mcpeek.execution import ExecutionEngine
    from src.mcpeek.transports.http import HTTPTransport
    from src.mcpeek.transports.stdio import STDIOTransport
    from src.mcpeek.formatters.json import JSONFormatter
    from src.mcpeek.utils.exceptions import MCPeekError
    from src.mcpeek.utils.logging import setup_logging
except ImportError as e:
    print(f"Error importing MCPeek modules: {e}")
    print("Make sure you're running from the correct directory and MCPeek is installed")
    sys.exit(1)

# Configuration
HOST = os.getenv("MCPEEK_HOST", "127.0.0.1")
PORT = int(os.getenv("MCPEEK_PORT", "8080"))
DEBUG = os.getenv("MCPEEK_DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("MCPEEK_LOG_LEVEL", "INFO")
CORS_ORIGINS = os.getenv("MCPEEK_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

# Setup logging
setup_logging(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# FastAPI application
app = FastAPI(
    title="MCPeek Web Interface",
    description="Badass hacker-themed MCP exploration interface",
    version="1.0.0",
    debug=DEBUG,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in-memory for now)
sessions: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class EndpointRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class DiscoverRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    verbosity: int = Field(1, ge=1, le=3, description="Verbosity level (1-3)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class ToolRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class ResourceRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    resource_uri: str = Field(..., description="URI of the resource to read")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class PromptRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    prompt_name: str = Field(..., description="Name of the prompt to get")
    arguments: Optional[Dict[str, Any]] = Field(None, description="Prompt arguments")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

# Utility functions
def create_config(endpoint: str, api_key: Optional[str] = None, auth_header: Optional[str] = None) -> Config:
    """Create a Config object for MCPeek operations."""
    config = Config(
        endpoint=endpoint,
        api_key=api_key,
        auth_header=auth_header,
        output_format="json",
        verbosity=1,
        timeout=30
    )
    return config

async def create_client(config: Config) -> MCPClient:
    """Create and initialize an MCP client."""
    auth_manager = AuthManager(config)
    
    # Determine transport type
    if config.endpoint.startswith(('http://', 'https://')):
        transport = HTTPTransport(config.endpoint, auth_manager)
    else:
        transport = STDIOTransport(config.endpoint)
    
    client = MCPClient(transport)
    await client.connect()
    return client

# API Routes

@app.get("/")
async def root():
    """Serve the main web interface."""
    # Return the hacker-themed HTML interface
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCPeek - Hacker Terminal</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Fira Code', monospace;
                background: #000;
                color: #00ff00;
                overflow: hidden;
                position: relative;
            }
            
            .matrix-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                opacity: 0.1;
            }
            
            .terminal {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100vh;
                background: rgba(0, 0, 0, 0.9);
                border: 2px solid #00ff00;
                border-radius: 10px;
                box-shadow: 0 0 20px #00ff00;
                display: flex;
                flex-direction: column;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .terminal-header {
                background: #001100;
                border-bottom: 1px solid #00ff00;
                padding: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .terminal-title {
                font-weight: 600;
                text-shadow: 0 0 10px #00ff00;
                animation: glow 2s ease-in-out infinite alternate;
            }
            
            @keyframes glow {
                from { text-shadow: 0 0 10px #00ff00; }
                to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
            }
            
            .terminal-controls {
                display: flex;
                gap: 10px;
            }
            
            .control-btn {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #ff0000;
                border: none;
                cursor: pointer;
            }
            
            .control-btn.minimize { background: #ffff00; }
            .control-btn.maximize { background: #00ff00; }
            
            .terminal-body {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                scrollbar-width: thin;
                scrollbar-color: #00ff00 #000;
            }
            
            .terminal-output {
                min-height: calc(100vh - 150px);
                white-space: pre-wrap;
                font-family: 'Fira Code', monospace;
            }
            
            .terminal-input {
                border-top: 1px solid #00ff00;
                padding: 10px;
                display: flex;
                align-items: center;
                background: #001100;
            }
            
            .prompt {
                color: #00ff00;
                margin-right: 10px;
                font-weight: 600;
            }
            
            .input-field {
                flex: 1;
                background: transparent;
                border: none;
                color: #00ff00;
                font-family: 'Fira Code', monospace;
                font-size: 14px;
                outline: none;
                caret-color: #00ff00;
            }
            
            .status-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #001100;
                border-top: 1px solid #00ff00;
                padding: 5px 20px;
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                z-index: 1000;
            }
            
            .loading {
                animation: blink 1s infinite;
            }
            
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
            
            .error {
                color: #ff0000;
                text-shadow: 0 0 10px #ff0000;
            }
            
            .success {
                color: #00ff00;
                text-shadow: 0 0 10px #00ff00;
            }
            
            .warning {
                color: #ffff00;
                text-shadow: 0 0 10px #ffff00;
            }
            
            .info {
                color: #00ffff;
                text-shadow: 0 0 10px #00ffff;
            }
            
            pre {
                color: #00ff00;
                font-family: 'Fira Code', monospace;
                font-size: 12px;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            
            .json-output {
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
                max-height: 400px;
                overflow-y: auto;
            }
            
            .help-panel {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 300px;
                background: rgba(0, 0, 0, 0.9);
                border: 2px solid #00ff00;
                border-radius: 10px;
                padding: 15px;
                font-size: 12px;
                z-index: 1001;
                display: none;
            }
            
            .help-panel.show {
                display: block;
                animation: slideIn 0.3s ease-out;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .help-title {
                color: #00ff00;
                font-weight: 600;
                margin-bottom: 10px;
                text-shadow: 0 0 10px #00ff00;
            }
            
            .help-command {
                color: #00ffff;
                font-weight: 500;
            }
            
            .help-desc {
                color: #00ff00;
                margin-bottom: 8px;
            }
        </style>
    </head>
    <body>
        <canvas class="matrix-bg" id="matrix"></canvas>
        
        <div class="terminal">
            <div class="terminal-header">
                <div class="terminal-title">MCPeek v1.0.0 - Hacker Terminal</div>
                <div class="terminal-controls">
                    <button class="control-btn"></button>
                    <button class="control-btn minimize"></button>
                    <button class="control-btn maximize"></button>
                </div>
            </div>
            
            <div class="terminal-body">
                <div class="terminal-output" id="output">
                    <div class="success">
███╗   ███╗ ██████╗██████╗ ███████╗███████╗██╗  ██╗
████╗ ████║██╔════╝██╔══██╗██╔════╝██╔════╝██║ ██╔╝
██╔████╔██║██║     ██████╔╝█████╗  █████╗  █████╔╝ 
██║╚██╔╝██║██║     ██╔═══╝ ██╔══╝  ██╔══╝  ██╔═██╗ 
██║ ╚═╝ ██║╚██████╗██║     ███████╗███████╗██║  ██╗
╚═╝     ╚═╝ ╚═════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝
                    </div>
                    <div class="info">
Welcome to MCPeek Web Interface - The Ultimate MCP Exploration Terminal
Type 'help' for available commands or start exploring MCP endpoints

<span class="warning">⚡ SYSTEM READY ⚡</span>
                    </div>
                </div>
            </div>
            
            <div class="terminal-input">
                <span class="prompt">mcpeek@terminal:~$</span>
                <input type="text" class="input-field" id="commandInput" placeholder="Enter command..." autocomplete="off">
            </div>
        </div>
        
        <div class="help-panel" id="helpPanel">
            <div class="help-title">Available Commands</div>
            <div class="help-desc"><span class="help-command">endpoint &lt;url&gt;</span> - Set MCP endpoint</div>
            <div class="help-desc"><span class="help-command">discover [-v|-vv|-vvv]</span> - Explore capabilities</div>
            <div class="help-desc"><span class="help-command">tool &lt;name&gt; [params]</span> - Execute tools</div>
            <div class="help-desc"><span class="help-command">resource &lt;uri&gt;</span> - Read resources</div>
            <div class="help-desc"><span class="help-command">prompt &lt;name&gt; [args]</span> - Get prompts</div>
            <div class="help-desc"><span class="help-command">auth &lt;key&gt;</span> - Set API key</div>
            <div class="help-desc"><span class="help-command">header &lt;auth&gt;</span> - Set auth header</div>
            <div class="help-desc"><span class="help-command">status</span> - Show current settings</div>
            <div class="help-desc"><span class="help-command">clear</span> - Clear terminal</div>
            <div class="help-desc"><span class="help-command">help</span> - Toggle this panel</div>
        </div>
        
        <div class="status-bar">
            <span id="statusText">Ready</span>
            <span id="timeDisplay"></span>
        </div>
        
        <script>
            // Matrix rain effect
            const canvas = document.getElementById('matrix');
            const ctx = canvas.getContext('2d');
            
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
            const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            const nums = '0123456789';
            const alphabet = katakana + latin + nums;
            
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            
            const rainDrops = [];
            
            for (let x = 0; x < columns; x++) {
                rainDrops[x] = 1;
            }
            
            const draw = () => {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#0F0';
                ctx.font = fontSize + 'px monospace';
                
                for (let i = 0; i < rainDrops.length; i++) {
                    const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                    ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                    
                    if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        rainDrops[i] = 0;
                    }
                    rainDrops[i]++;
                }
            };
            
            setInterval(draw, 30);
            
            // Terminal functionality
            const output = document.getElementById('output');
            const input = document.getElementById('commandInput');
            const statusText = document.getElementById('statusText');
            const timeDisplay = document.getElementById('timeDisplay');
            const helpPanel = document.getElementById('helpPanel');
            
            let currentEndpoint = '';
            let currentApiKey = '';
            let currentAuthHeader = '';
            let commandHistory = [];
            let historyIndex = -1;
            
            // Update time display
            setInterval(() => {
                const now = new Date();
                timeDisplay.textContent = now.toLocaleTimeString();
            }, 1000);
            
            // Command processing
            const processCommand = async (command) => {
                const parts = command.trim().split(' ');
                const cmd = parts[0].toLowerCase();
                const args = parts.slice(1);
                
                addOutput(`<span class="prompt">mcpeek@terminal:~$</span> ${command}`);
                
                try {
                    switch (cmd) {
                        case 'help':
                            helpPanel.classList.toggle('show');
                            break;
                            
                        case 'clear':
                            output.innerHTML = '';
                            break;
                            
                        case 'endpoint':
                            if (args.length === 0) {
                                addOutput('<span class="error">Usage: endpoint <url></span>');
                                return;
                            }
                            currentEndpoint = args[0];
                            addOutput(`<span class="success">Endpoint set to: ${currentEndpoint}</span>`);
                            updateStatus(`Connected to ${currentEndpoint}`);
                            break;
                            
                        case 'auth':
                            if (args.length === 0) {
                                addOutput('<span class="error">Usage: auth <api-key></span>');
                                return;
                            }
                            currentApiKey = args[0];
                            addOutput('<span class="success">API key set</span>');
                            break;
                            
                        case 'header':
                            if (args.length === 0) {
                                addOutput('<span class="error">Usage: header <auth-header></span>');
                                return;
                            }
                            currentAuthHeader = args.join(' ');
                            addOutput('<span class="success">Auth header set</span>');
                            break;
                            
                        case 'status':
                            addOutput(`<span class="info">Current Configuration:</span>`);
                            addOutput(`  Endpoint: ${currentEndpoint || 'Not set'}`);
                            addOutput(`  API Key: ${currentApiKey ? 'Set' : 'Not set'}`);
                            addOutput(`  Auth Header: ${currentAuthHeader ? 'Set' : 'Not set'}`);
                            break;
                            
                        case 'discover':
                            await executeDiscover(args);
                            break;
                            
                        case 'tool':
                            await executeTool(args);
                            break;
                            
                        case 'resource':
                            await executeResource(args);
                            break;
                            
                        case 'prompt':
                            await executePrompt(args);
                            break;
                            
                        default:
                            addOutput(`<span class="error">Unknown command: ${cmd}</span>`);
                            addOutput('<span class="info">Type "help" for available commands</span>');
                    }
                } catch (error) {
                    addOutput(`<span class="error">Error: ${error.message}</span>`);
                }
            };
            
            const executeDiscover = async (args) => {
                if (!currentEndpoint) {
                    addOutput('<span class="error">No endpoint set. Use: endpoint <url></span>');
                    return;
                }
                
                let verbosity = 1;
                if (args.includes('-v')) verbosity = 1;
                else if (args.includes('-vv')) verbosity = 2;
                else if (args.includes('-vvv')) verbosity = 3;
                
                updateStatus('Discovering capabilities...');
                addOutput('<span class="info">🔍 Discovering MCP capabilities...</span>');
                
                try {
                    const response = await fetch('/api/discover', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            endpoint: currentEndpoint,
                            verbosity: verbosity,
                            api_key: currentApiKey || null,
                            auth_header: currentAuthHeader || null
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        addOutput('<span class="success">✅ Discovery complete!</span>');
                        addJsonOutput(result);
                    } else {
                        addOutput(`<span class="error">❌ Discovery failed: ${result.detail}</span>`);
                    }
                } catch (error) {
                    addOutput(`<span class="error">❌ Request failed: ${error.message}</span>`);
                } finally {
                    updateStatus('Ready');
                }
            };
            
            const executeTool = async (args) => {
                if (!currentEndpoint) {
                    addOutput('<span class="error">No endpoint set. Use: endpoint <url></span>');
                    return;
                }
                
                if (args.length === 0) {
                    addOutput('<span class="error">Usage: tool <name> [json-parameters]</span>');
                    return;
                }
                
                const toolName = args[0];
                let parameters = {};
                
                if (args.length > 1) {
                    try {
                        parameters = JSON.parse(args.slice(1).join(' '));
                    } catch (e) {
                        addOutput('<span class="error">Invalid JSON parameters</span>');
                        return;
                    }
                }
                
                updateStatus(`Executing tool: ${toolName}...`);
                addOutput(`<span class="info">🔧 Executing tool: ${toolName}</span>`);
                
                try {
                    const response = await fetch('/api/tool', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            endpoint: currentEndpoint,
                            tool_name: toolName,
                            parameters: parameters,
                            api_key: currentApiKey || null,
                            auth_header: currentAuthHeader || null
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        addOutput('<span class="success">✅ Tool executed successfully!</span>');
                        addJsonOutput(result);
                    } else {
                        addOutput(`<span class="error">❌ Tool execution failed: ${result.detail}</span>`);
                    }
                } catch (error) {
                    addOutput(`<span class="error">❌ Request failed: ${error.message}</span>`);
                } finally {
                    updateStatus('Ready');
                }
            };
            
            const executeResource = async (args) => {
                if (!currentEndpoint) {
                    addOutput('<span class="error">No endpoint set. Use: endpoint <url></span>');
                    return;
                }
                
                if (args.length === 0) {
                    addOutput('<span class="error">Usage: resource <uri></span>');
                    return;
                }
                
                const resourceUri = args[0];
                
                updateStatus(`Reading resource: ${resourceUri}...`);
                addOutput(`<span class="info">📖 Reading resource: ${resourceUri}</span>`);
                
                try {
                    const response = await fetch('/api/resource', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            endpoint: currentEndpoint,
                            resource_uri: resourceUri,
                            api_key: currentApiKey || null,
                            auth_header: currentAuthHeader || null
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        addOutput('<span class="success">✅ Resource read successfully!</span>');
                        addJsonOutput(result);
                    } else {
                        addOutput(`<span class="error">❌ Resource read failed: ${result.detail}</span>`);
                    }
                } catch (error) {
                    addOutput(`<span class="error">❌ Request failed: ${error.message}</span>`);
                } finally {
                    updateStatus('Ready');
                }
            };
            
            const executePrompt = async (args) => {
                if (!currentEndpoint) {
                    addOutput('<span class="error">No endpoint set. Use: endpoint <url></span>');
                    return;
                }
                
                if (args.length === 0) {
                    addOutput('<span class="error">Usage: prompt <name> [json-arguments]</span>');
                    return;
                }
                
                const promptName = args[0];
                let arguments = {};
                
                if (args.length > 1) {
                    try {
                        arguments = JSON.parse(args.slice(1).join(' '));
                    } catch (e) {
                        addOutput('<span class="error">Invalid JSON arguments</span>');
                        return;
                    }
                }
                
                updateStatus(`Getting prompt: ${promptName}...`);
                addOutput(`<span class="info">💬 Getting prompt: ${promptName}</span>`);
                
                try {
                    const response = await fetch('/api/prompt', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            endpoint: currentEndpoint,
                            prompt_name: promptName,
                            arguments: arguments,
                            api_key: currentApiKey || null,
                            auth_header: currentAuthHeader || null
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        addOutput('<span class="success">✅ Prompt retrieved successfully!</span>');
                        addJsonOutput(result);
                    } else {
                        addOutput(`<span class="error">❌ Prompt retrieval failed: ${result.detail}</span>`);
                    }
                } catch (error) {
                    addOutput(`<span class="error">❌ Request failed: ${error.message}</span>`);
                } finally {
                    updateStatus('Ready');
                }
            };
            
            const addOutput = (text) => {
                output.innerHTML += text + '\\n';
                output.scrollTop = output.scrollHeight;
            };
            
            const addJsonOutput = (data) => {
                const jsonStr = JSON.stringify(data, null, 2);
                output.innerHTML += `<div class="json-output"><pre>${jsonStr}</pre></div>`;
                output.scrollTop = output.scrollHeight;
            };
            
            const updateStatus = (status) => {
                statusText.textContent = status;
                if (status.includes('...')) {
                    statusText.classList.add('loading');
                } else {
                    statusText.classList.remove('loading');
                }
            };
            
            // Input handling
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const command = input.value.trim();
                    if (command) {
                        commandHistory.push(command);
                        historyIndex = commandHistory.length;
                        processCommand(command);
                    }
                    input.value = '';
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (historyIndex > 0) {
                        historyIndex--;
                        input.value = commandHistory[historyIndex];
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (historyIndex < commandHistory.length - 1) {
                        historyIndex++;
                        input.value = commandHistory[historyIndex];
                    } else {
                        historyIndex = commandHistory.length;
                        input.value = '';
                    }
                } else if (e.key === 'Tab') {
                    e.preventDefault();
                    // Basic tab completion
                    const commands = ['endpoint', 'discover', 'tool', 'resource', 'prompt', 'auth', 'header', 'status', 'clear', 'help'];
                    const partial = input.value.toLowerCase();
                    const matches = commands.filter(cmd => cmd.startsWith(partial));
                    if (matches.length === 1) {
                        input.value = matches[0];
                    }
                }
            });
            
            // Focus input on page load
            input.focus();
            
            // Resize canvas on window resize
            window.addEventListener('resize', () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "ok", "message": "MCPeek Web Interface is running"}

@app.post("/api/discover")
@limiter.limit("10/minute")
async def discover_endpoint(request: Request, discover_request: DiscoverRequest):
    """Discover MCP endpoint capabilities."""
    try:
        config = create_config(
            discover_request.endpoint,
            discover_request.api_key,
            discover_request.auth_header
        )
        config.verbosity = discover_request.verbosity
        
        client = await create_client(config)
        
        try:
            discovery_engine = DiscoveryEngine(client, JSONFormatter())
            result = await discovery_engine.discover()
            return JSONResponse(content=result)
        finally:
            await client.disconnect()
            
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tool")
@limiter.limit("20/minute")
async def execute_tool(request: Request, tool_request: ToolRequest):
    """Execute an MCP tool."""
    try:
        config = create_config(
            tool_request.endpoint,
            tool_request.api_key,
            tool_request.auth_header
        )
        
        client = await create_client(config)
        
        try:
            execution_engine = ExecutionEngine(client, JSONFormatter())
            result = await execution_engine.execute_tool(
                tool_request.tool_name,
                tool_request.parameters or {}
            )
            return JSONResponse(content=result)
        finally:
            await client.disconnect()
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resource")
@limiter.limit("20/minute")
async def read_resource(request: Request, resource_request: ResourceRequest):
    """Read an MCP resource."""
    try:
        config = create_config(
            resource_request.endpoint,
            resource_request.api_key,
            resource_request.auth_header
        )
        
        client = await create_client(config)
        
        try:
            execution_engine = ExecutionEngine(client, JSONFormatter())
            result = await execution_engine.read_resource(resource_request.resource_uri)
            return JSONResponse(content=result)
        finally:
            await client.disconnect()
            
    except Exception as e:
        logger.error(f"Resource read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompt")
@limiter.limit("20/minute")
async def get_prompt(request: Request, prompt_request: PromptRequest):
    """Get an MCP prompt."""
    try:
        config = create_config(
            prompt_request.endpoint,
            prompt_request.api_key,
            prompt_request.auth_header
        )
        
        client = await create_client(config)
        
        try:
            execution_engine = ExecutionEngine(client, JSONFormatter())
            result = await execution_engine.get_prompt(
                prompt_request.prompt_name,
                prompt_request.arguments or {}
            )
            return JSONResponse(content=result)
        finally:
            await client.disconnect()
            
    except Exception as e:
        logger.error(f"Prompt retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting MCPeek Web Interface on {HOST}:{PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")
    
    try:
        uvicorn.run(
            "app:app",
            host=HOST,
            port=PORT,
            log_level=LOG_LEVEL.lower(),
            reload=DEBUG,
            access_log=DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Shutting down MCPeek Web Interface...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)