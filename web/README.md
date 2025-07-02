# MCPeek Web Interface 🚀💀

**Badass hacker-themed terminal web interface for MCP exploration**

A complete web-based terminal interface that brings the power of MCPeek to your browser with a cyberpunk aesthetic inspired by Mr. Robot and The Matrix.

## ✨ Features

### 🎮 Terminal Interface
- **Full command-line emulator** with history and auto-completion
- **Matrix rain background** with animated falling characters
- **Cyberpunk styling** - green-on-black with glow effects
- **Command history** with arrow key navigation
- **Tab completion** for available commands
- **Real-time status monitoring**

### 🔧 MCP Operations
- **Endpoint discovery** with multiple verbosity levels
- **Tool execution** with JSON parameter support
- **Resource reading** from MCP endpoints
- **Prompt interaction** with custom arguments
- **Authentication support** (API keys & custom headers)
- **Session management** and connection pooling

### 🎨 Visual Design
- **Monospace fonts** (Fira Code, JetBrains Mono)
- **Matrix aesthetic** with green terminal colors
- **Animated backgrounds** and glitch effects
- **Responsive design** for desktop and mobile
- **Status indicators** with live system monitoring
- **Help panel** with command reference

## 🚀 Quick Start

### Method 1: Startup Script (Recommended)
```bash
cd web
./start.sh
```

### Method 2: Manual Installation
```bash
# Backend
cd web
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run build
cd ..

# Start server
cd backend
python app.py
```

### Method 3: Development Mode
```bash
# Terminal 1: Backend
cd web/backend
pip install -r ../requirements.txt
python app.py

# Terminal 2: Frontend (dev server)
cd web/frontend
npm install
npm run dev
```

## 🌐 Access

- **Production**: http://localhost:8080
- **Development**: http://localhost:3000 (frontend dev server)
- **API Docs**: http://localhost:8080/api/docs (debug mode)

## 🎯 Terminal Commands

### Configuration Commands
```bash
endpoint <url>                 # Set MCP endpoint
auth <api-key>                 # Set API key authentication
header <auth-header>           # Set custom authorization header
status                         # Show current configuration
```

### MCP Commands
```bash
discover [-v|-vv|-vvv]        # Explore endpoint capabilities
tool <name> [json-params]     # Execute MCP tools
resource <uri>                # Read MCP resources
prompt <name> [json-args]     # Get MCP prompts
```

### Terminal Commands
```bash
help                          # Toggle help panel
clear                         # Clear terminal output
```

## 💡 Usage Examples

### Basic Setup
```bash
# Set your MCP endpoint
endpoint http://localhost:8000/mcp

# Optional: Add authentication
auth your_api_key_here

# Discover capabilities
discover -v
```

### Tool Execution
```bash
# List available tools first
discover -v

# Execute a tool without parameters
tool list_files

# Execute a tool with JSON parameters
tool search_files {"pattern": "*.py", "path": "/src"}
```

### Resource Access
```bash
# Read a file resource
resource file:///path/to/file.txt

# Read a web resource
resource http://example.com/api/data
```

### Prompt Interaction
```bash
# Get a prompt without arguments
prompt summarize

# Get a prompt with JSON arguments
prompt analyze_code {"language": "python", "complexity": "high"}
```

## 🏗️ Architecture

### Backend (FastAPI)
- **REST API** exposing all MCPeek functionality
- **Session management** for connection pooling
- **Authentication handling** for API keys and headers
- **Error handling** with detailed error messages
- **CORS support** for frontend integration

### Frontend (React + TypeScript)
- **Terminal emulator** with full command-line interface
- **Styled Components** for dynamic styling
- **Axios** for API communication
- **Matrix rain effect** with Canvas API
- **Responsive design** with mobile support

### Key Components
- `Terminal.tsx` - Main terminal interface with command handling
- `MatrixRain.tsx` - Animated background effect
- `Header.tsx` - Status bar with system information
- `StatusBar.tsx` - Connection and performance monitoring
- `api.ts` - API client for backend communication

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the web directory:

```bash
# Server Configuration
MCPEEK_HOST=127.0.0.1
MCPEEK_PORT=8080

# Logging
MCPEEK_LOG_LEVEL=INFO
MCPEEK_DEBUG=false

# CORS Origins
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Optional Defaults
MCPEEK_API_KEY=your_default_api_key
MCPEEK_DEFAULT_ENDPOINT=http://localhost:8000/mcp
```

### Frontend Configuration
Modify `vite.config.ts` for custom proxy settings:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8080',
      changeOrigin: true
    }
  }
}
```

## 🎨 Customization

### Terminal Colors
Edit `GlobalStyle.ts` to customize the color scheme:

```typescript
// Primary colors
const GREEN = '#00ff00'  // Matrix green
const BLACK = '#000000'  // Background
const CYAN = '#00ffff'   // Commands
```

### Matrix Rain
Modify `MatrixRain.tsx` to customize the background effect:

```typescript
// Character set
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789...'

// Animation speed
const interval = setInterval(draw, 50) // milliseconds
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check `MCPEEK_CORS_ORIGINS` in `.env`
   - Ensure frontend URL is included

2. **Connection Failed**
   - Verify backend is running on correct port
   - Check firewall settings
   - Ensure MCP endpoint is accessible

3. **Command Not Found**
   - Check endpoint configuration
   - Verify MCP server is running
   - Use `discover` to list available commands

4. **Build Failures**
   - Ensure Node.js 16+ is installed
   - Clear `node_modules` and reinstall
   - Check for TypeScript errors

### Debug Mode
Enable debug mode for detailed logging:

```bash
export MCPEEK_DEBUG=true
export MCPEEK_LOG_LEVEL=DEBUG
```

## 🔒 Security

- **No credentials stored** in browser localStorage
- **HTTPS support** for production deployments
- **CORS protection** with configurable origins
- **Input validation** for all commands
- **Session timeout** for inactive connections

## 📦 Dependencies

### Backend
- `fastapi` - Modern web framework
- `uvicorn` - ASGI server
- `aiohttp` - Async HTTP client
- `pydantic` - Data validation

### Frontend
- `react` - UI framework
- `typescript` - Type safety
- `styled-components` - CSS-in-JS
- `axios` - HTTP client
- `vite` - Build tool

## 🎪 Easter Eggs

- **Matrix rain background** with Japanese characters
- **Glitch effects** on logo hover
- **Terminal boot sequence** with ASCII art
- **Pulsing status indicators**
- **Command history persistence**
- **Tab completion** for commands

---

**Built with 💚 by the MCPeek team**

*"Welcome to the matrix of MCP exploration"*