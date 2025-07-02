# MCPeek Web Interface 💀⚡

**The Ultimate Badass Hacker-Themed MCP Exploration Terminal**

A cyberpunk-inspired web interface for MCPeek that brings Matrix-style aesthetics to MCP (Model Context Protocol) exploration.

## 🎯 Features

### 🌟 Core Functionality
- **Complete MCP Integration**: All MCPeek CLI functionality exposed via REST API
- **Real-time Operations**: Live MCP discovery, tool execution, resource reading, and prompt retrieval
- **Multi-endpoint Support**: Connect to and switch between multiple MCP endpoints
- **Authentication Support**: API keys and custom authorization headers
- **Session Management**: Persistent connections and configuration

### 🎨 Visual Design
- **Matrix Rain Background**: Animated falling green characters for ultimate hacker vibes
- **Terminal Interface**: Full command-line emulator with history and auto-completion
- **Cyberpunk Styling**: Green-on-black color scheme with Fira Code monospace fonts
- **Glow Effects**: Text shadows, animations, and visual indicators
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🎮 Terminal Commands
```bash
endpoint <url>                 # Set MCP endpoint
discover [-v|-vv|-vvv]        # Explore capabilities (with verbosity levels)
tool <name> [json-params]     # Execute MCP tools
resource <uri>                # Read MCP resources
prompt <name> [json-args]     # Get MCP prompts
auth <api-key>                # Set authentication
header <auth-header>          # Set custom headers
status                        # Show current settings
clear                         # Clear terminal
help                          # Toggle help panel
```

### 🔧 Advanced Features
- **Command History**: Arrow key navigation through previous commands
- **Tab Completion**: Auto-completion for available commands
- **Help System**: Toggle help panel with all commands and usage
- **Status Monitoring**: Live connection status, system stats, and uptime
- **Error Handling**: Comprehensive error messages and debugging
- **Rate Limiting**: Built-in API rate limiting for stability

## 🚀 Quick Start

### Method 1: Easy Startup Script
```bash
cd web && ./start.sh
```

### Method 2: With pip
```bash
pip install -e .[web]
mcpeek-web
```

### Method 3: Manual Setup
```bash
cd web

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (optional - interface is served by backend)
cd frontend
npm install
npm run build
cd ..

# Start server
cd backend
python app.py
```

## 🌐 Access

Once started, access the interface at:
**http://localhost:8080**

## 🎪 Usage Examples

### Basic MCP Discovery
```bash
# Set endpoint
endpoint http://localhost:8000/mcp

# Discover capabilities
discover -vv

# Execute a tool
tool "list_files" {"path": "/"}

# Read a resource
resource "file:///path/to/file.txt"

# Get a prompt
prompt "analyze_code" {"language": "python"}
```

### Authentication
```bash
# Set API key
auth sk-1234567890abcdef

# Or set custom auth header
header "Bearer your-token-here"

# Check current settings
status
```

## 🏗️ Architecture

### Backend (FastAPI)
- **REST API**: Clean endpoints for all MCP operations
- **Session Management**: In-memory session storage for multiple connections
- **Authentication**: Support for API keys and custom headers
- **Rate Limiting**: Built-in protection against abuse
- **Error Handling**: Comprehensive exception handling and logging

### Frontend (React + TypeScript)
- **Single Page Application**: Complete terminal interface
- **Styled Components**: Modular, themeable components
- **Real-time Updates**: Live status monitoring and feedback
- **Responsive Design**: Mobile-friendly interface

### Transport Layer
- **HTTP Transport**: For HTTP/HTTPS MCP endpoints
- **STDIO Transport**: For local subprocess MCP servers
- **Connection Pooling**: Efficient resource management

## 🔧 Configuration

### Environment Variables
```bash
# Server Configuration
MCPEEK_HOST=127.0.0.1           # Server host
MCPEEK_PORT=8080                # Server port
MCPEEK_LOG_LEVEL=INFO           # Logging level
MCPEEK_DEBUG=false              # Debug mode

# CORS Configuration
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Optional MCP Configuration
MCPEEK_DEFAULT_ENDPOINT=http://localhost:8000/mcp
MCPEEK_API_KEY=your-api-key-here
MCPEEK_AUTH_HEADER=Bearer your-token-here
```

### Custom Configuration
1. Copy `.env.example` to `.env`
2. Edit `.env` with your preferred settings
3. Restart the server

## 🎨 Visual Inspiration

The interface design draws inspiration from:
- **Mr. Robot**: Terminal-focused hacker aesthetic
- **The Matrix**: Green-on-black color scheme and rain effect
- **Cyberpunk 2077**: Futuristic UI elements and glow effects
- **Classic Terminals**: Monospace fonts and command-line interface

## 🔍 API Documentation

### Endpoints

#### Health Check
```
GET /api/health
```

#### Discovery
```
POST /api/discover
{
  "endpoint": "http://localhost:8000/mcp",
  "verbosity": 2,
  "api_key": "optional",
  "auth_header": "optional"
}
```

#### Tool Execution
```
POST /api/tool
{
  "endpoint": "http://localhost:8000/mcp",
  "tool_name": "list_files",
  "parameters": {"path": "/"},
  "api_key": "optional",
  "auth_header": "optional"
}
```

#### Resource Reading
```
POST /api/resource
{
  "endpoint": "http://localhost:8000/mcp",
  "resource_uri": "file:///path/to/file.txt",
  "api_key": "optional",
  "auth_header": "optional"
}
```

#### Prompt Retrieval
```
POST /api/prompt
{
  "endpoint": "http://localhost:8000/mcp",
  "prompt_name": "analyze_code",
  "arguments": {"language": "python"},
  "api_key": "optional",
  "auth_header": "optional"
}
```

## 🛠️ Development

### Project Structure
```
web/
├── backend/               # FastAPI backend
│   └── app.py            # Main application
├── frontend/             # React frontend
│   ├── src/              # Source code
│   ├── package.json      # Dependencies
│   └── vite.config.ts    # Build configuration
├── start.sh              # Startup script
├── requirements.txt      # Python dependencies
├── .env.example          # Configuration template
└── README.md             # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🎯 Roadmap

### Planned Features
- [ ] WebSocket support for real-time updates
- [ ] Multiple terminal tabs/sessions
- [ ] Command history persistence
- [ ] Custom themes and color schemes
- [ ] Plugin system for custom commands
- [ ] Export/import functionality for sessions
- [ ] Integration with popular MCP servers

### Known Issues
- Sessions are stored in memory (lost on restart)
- No authentication for the web interface itself
- Limited to single-user usage

## 🎉 Credits

Created with ❤️ and 💀 by the MCPeek team.

Special thanks to the cyberpunk and hacker aesthetic communities for inspiration.

## 📄 License

MIT License - see the main project LICENSE file for details.

---

**💀 Welcome to the Matrix, Neo. Time to explore some MCPs. ⚡**