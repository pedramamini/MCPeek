# MCPeek Web Interface - Hacker Terminal 💀

A badass, terminal-style web interface for MCPeek with Mr. Robot aesthetics. Experience MCP exploration like a true hacker.

## 🎯 Features

- **Terminal Interface**: Full command-line experience in your browser
- **Matrix Rain Effect**: Animated background for ultimate hacker vibes
- **Real-time Operations**: Live MCP discovery, tool execution, and more
- **Command History**: Navigate through previous commands with arrow keys
- **Auto-completion**: Tab completion for MCPeek commands
- **Authentication Support**: API keys and custom headers
- **Multiple Endpoints**: Manage and switch between MCP endpoints
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Method 1: Easy Startup Script
```bash
cd web
./start.sh
```

### Method 2: Install with pip
```bash
# Install MCPeek with web dependencies
pip install -e .[web]

# Start the web interface
mcpeek-web
```

### Method 3: Manual Setup
```bash
# Install Python dependencies
cd web
pip install -r requirements.txt
pip install -e ..

# Install and build React frontend
cd frontend
npm install
npm run build
cd ..

# Start the backend server
cd backend
python app.py
```

## 🌐 Access

Open your browser and navigate to: **http://localhost:8080**

## 🎮 Terminal Commands

The web interface supports all MCPeek functionality through terminal commands:

### Connection Management
```bash
endpoint <url>                 # Set MCP endpoint URL
auth <api-key>                # Set API key for authentication
header <auth-header>          # Set custom authentication header
timeout <seconds>             # Set connection timeout
status                        # Show current settings
```

### MCP Operations
```bash
discover [-v|-vv|-vvv]        # Explore endpoint capabilities
                              # -v: brief, -vv: detailed, -vvv: full schema

tool <name> [json-params]     # Execute MCP tool
                              # Example: tool search {"query": "hello"}

resource <uri>                # Read MCP resource
                              # Example: resource file:///path/to/file

prompt <name> [json-params]   # Get MCP prompt
                              # Example: prompt analyze {"data": "sample"}
```

### Interface Commands
```bash
help                          # Toggle help panel
clear                         # Clear terminal history
```

## 🎨 Visual Design

The interface features a cyberpunk/hacker aesthetic inspired by Mr. Robot:

- **Colors**: Matrix green (#00ff00) on pure black (#000000)
- **Typography**: Fira Code monospace font with text shadows and glow effects
- **Background**: Subtle Matrix rain animation
- **Effects**: Glitch animations, pulsing indicators, neon glow
- **Layout**: Terminal-style with command prompt and scrolling output

## 🛠️ Architecture

### Backend (FastAPI)
- **File**: `backend/app.py`
- **Port**: 8080
- **Features**: REST API exposing all MCPeek functionality
- **Endpoints**:
  - `POST /api/discover` - MCP endpoint discovery
  - `POST /api/tool` - Tool execution
  - `POST /api/resource` - Resource reading
  - `POST /api/prompt` - Prompt retrieval
  - `GET /api/health` - Health check

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Styled-components with CSS-in-JS
- **Features**: Terminal emulator, command history, auto-completion
- **Components**:
  - `App.tsx` - Main application container
  - `Terminal.tsx` - Command-line interface
  - `StatusBar.tsx` - System status and stats
  - `MatrixRain.tsx` - Background animation effect

## 📱 Usage Examples

### Basic Discovery
```bash
# Set endpoint
endpoint http://localhost:8000/mcp

# Discover capabilities
discover -v
```

### Tool Execution
```bash
# Set endpoint and auth
endpoint https://api.example.com/mcp
auth your-api-key-here

# Execute a tool with parameters
tool file_search {"path": "/home", "pattern": "*.py"}
```

### Resource Access
```bash
# Read a resource
resource file:///etc/hosts

# Read with authentication
header "Bearer your-token"
resource https://api.example.com/data
```

## 🎯 Keyboard Shortcuts

- **Enter**: Execute command
- **↑/↓ Arrow Keys**: Navigate command history
- **Tab**: Auto-complete commands
- **Ctrl+C**: (Terminal shortcut - handled by browser)

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm start  # Start development server on port 3000
```

### Backend Development
```bash
cd backend
uvicorn app:app --reload --port 8080
```

## 🎭 Customization

The interface is highly customizable through styled-components. Key visual elements:

- **Colors**: Modify color constants in components
- **Fonts**: Change font family in GlobalStyle
- **Animations**: Adjust keyframe animations
- **Matrix Effect**: Customize MatrixRain component parameters

## 🚨 Security Notes

- The web interface runs locally by default
- For production deployment, configure CORS properly
- Use HTTPS for remote MCP endpoints
- Never expose API keys in client-side code

## 🎪 Easter Eggs

- Glitch effect on logo hover
- Matrix rain responds to activity
- ASCII art loading screen
- Hacker-style system stats

Enjoy the most badass MCP exploration experience! 💀⚡