# MCPeek Web Interface 🚀

A badass hacker-themed terminal web interface for exploring Model Context Protocol (MCP) endpoints.

## Features ⚡

- **Terminal-Style Interface**: Full command-line emulator with history and auto-completion
- **Matrix Rain Background**: Animated falling green characters for ultimate hacker vibes  
- **Cyberpunk Styling**: Green-on-black with Fira Code fonts, glow effects, and animations
- **Real-time MCP Operations**: Live discovery, tool execution, resource reading, and prompt interaction
- **Authentication Support**: API keys and custom authorization headers
- **Status Monitoring**: Live system stats, connection status, and uptime tracking
- **Help System**: Interactive help panel with all commands and shortcuts
- **Responsive Design**: Works perfectly on desktop and mobile

## Quick Start 🎯

### Method 1: Use Startup Script (Recommended)
```bash
cd web && ./start.sh
```

### Method 2: Install with pip
```bash
pip install -e .[web]
mcpeek-web
```

### Method 3: Manual Setup
```bash
cd web

# Install Python dependencies
pip install -r requirements.txt

# Install and build frontend
cd frontend
npm install
npm run build
cd ..

# Start backend server
cd backend
python app.py
```

## Access 🌐

- **Web Interface**: http://localhost:8080
- **API Documentation**: http://localhost:8080/api/docs
- **Interactive API**: http://localhost:8080/api/redoc

## Terminal Commands 🎮

### Connection Commands
- `endpoint <url>` - Set MCP endpoint URL
- `auth <api-key>` - Set API key for authentication  
- `header <auth-header>` - Set custom authorization header
- `status` - Show current connection and auth status

### MCP Operations
- `discover [-v|-vv|-vvv]` - Explore endpoint capabilities (with verbosity levels)
- `tool <name> [json-params]` - Execute MCP tools
- `resource <uri>` - Read MCP resources
- `prompt <name> [json-args]` - Get MCP prompts

### Terminal Commands
- `clear` - Clear terminal output
- `help` - Toggle help panel

### Keyboard Shortcuts
- `↑/↓` - Navigate command history
- `Tab` - Auto-complete commands
- `Enter` - Execute command
- `Ctrl+C` - Cancel operation
- `Ctrl+L` - Clear terminal
- `Esc` - Close help panel

## Example Usage 💡

```bash
# Connect to an MCP endpoint
$ endpoint http://localhost:8000/mcp

# Set authentication
$ auth your-api-key-here

# Discover capabilities
$ discover -v

# Execute a tool
$ tool search {"query": "hello world", "limit": 10}

# Read a resource
$ resource file://path/to/document.txt

# Get a prompt
$ prompt summarize {"text": "Long text to summarize"}

# Check status
$ status
```

## Configuration ⚙️

The web interface can be configured via environment variables:

```bash
# Server Configuration
MCPEEK_WEB_HOST=127.0.0.1
MCPEEK_WEB_PORT=8080

# Logging
MCPEEK_LOG_LEVEL=INFO
MCPEEK_DEBUG=false

# CORS (for development)
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Optional: Default endpoint and auth
MCPEEK_DEFAULT_ENDPOINT=http://localhost:8000/mcp
MCPEEK_DEFAULT_API_KEY=your-api-key
```

## Architecture 🏗️

### Backend (FastAPI)
- **REST API**: Exposes all MCPeek functionality via clean endpoints
- **Session Management**: Connection pooling for multiple MCP endpoints
- **Authentication**: Support for API keys and custom headers
- **Error Handling**: Comprehensive error messages and debugging
- **CORS Support**: Proper cross-origin handling for frontend

### Frontend (React + TypeScript)
- **Terminal Emulator**: Full command-line interface with history
- **Matrix Rain**: Animated background with Japanese characters
- **Styled Components**: Cyberpunk styling with green-on-black theme
- **Status Bar**: Live monitoring of connections and system stats
- **Help Panel**: Interactive documentation and command reference

### Key Files
```
web/
├── start.sh              # Main startup script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment configuration template
├── mcpeek-web           # Pip entry point script
├── backend/
│   └── app.py           # FastAPI server
└── frontend/
    ├── package.json     # Node.js dependencies
    ├── vite.config.ts   # Build configuration
    ├── src/
    │   ├── App.tsx      # Main React app
    │   ├── components/  # React components
    │   │   ├── Terminal.tsx     # Terminal interface
    │   │   ├── MatrixRain.tsx   # Background animation
    │   │   ├── StatusBar.tsx    # Status monitoring
    │   │   └── HelpPanel.tsx    # Help documentation
    │   └── index.css    # Global styles
    └── dist/            # Built frontend files
```

## Development 🛠️

### Frontend Development
```bash
cd web/frontend
npm run dev
```

### Backend Development
```bash
cd web/backend
MCPEEK_DEBUG=true python app.py
```

### Building for Production
```bash
cd web/frontend
npm run build
```

## Troubleshooting 🔧

### Common Issues

**npm ci error**: If you get "package-lock.json not found", the startup script will automatically use `npm install` instead.

**Port already in use**: Change the port with `MCPEEK_WEB_PORT=8081`

**CORS errors**: Make sure your MCP endpoint allows requests from the web interface origin.

**Authentication errors**: Verify your API key and endpoint URL are correct.

### Debug Mode
```bash
MCPEEK_DEBUG=true ./start.sh
```

## Visual Design 🎨

The interface features a complete cyberpunk/hacker aesthetic:

- **Matrix Rain**: Animated falling Japanese characters background
- **Terminal Styling**: Green-on-black with monospace Fira Code fonts  
- **Glow Effects**: Text shadows and neon glowing elements
- **Window Controls**: Terminal-style window with colored control buttons
- **Status Monitoring**: Live system stats with pulsing connection indicators
- **Glitch Animations**: Hover effects and loading animations
- **Responsive Layout**: Works on all screen sizes

This creates the ultimate Mr. Robot / Matrix hacker experience for exploring MCP endpoints! 💀⚡

## License 📄

MIT License - See main project LICENSE file.