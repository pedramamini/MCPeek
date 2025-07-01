# MCPeek Web Interface

A badass hacker-themed web interface for MCPeek with a Mr. Robot aesthetic.

## Features

- **Terminal Interface**: Full-featured terminal emulator with command history and auto-completion
- **Matrix Rain Effect**: Animated background with falling green characters
- **Cyberpunk Styling**: Green-on-black color scheme with monospace fonts and glitch effects
- **Real-time Operations**: Execute MCP commands with live results
- **Responsive Design**: Works on desktop and mobile devices
- **Status Monitoring**: Live system status and connection monitoring

## Architecture

### Backend (FastAPI)
- **FastAPI Server**: REST API exposing MCPeek functionality
- **Async Operations**: Non-blocking MCP operations
- **Error Handling**: Comprehensive error management
- **CORS Support**: Cross-origin resource sharing for development

### Frontend (React)
- **Terminal Component**: Interactive command-line interface
- **Matrix Rain**: Animated background effect
- **Status Bar**: System monitoring and clock
- **Styled Components**: CSS-in-JS with animations

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Install backend dependencies
cd web
pip install -r requirements.txt

# Start the API server
python backend/app.py
```

### Frontend Setup
```bash
# Install frontend dependencies
cd web/frontend
npm install

# Start development server
npm start
```

### Production Build
```bash
# Build frontend for production
cd web/frontend
npm run build

# The backend will serve the built frontend automatically
```

## API Endpoints

### Discovery
```
POST /api/discover
{
  "endpoint": "http://localhost:8000/mcp",
  "verbosity": 2,
  "tool_tickle": false,
  "api_key": "optional",
  "auth_header": "optional"
}
```

### Tool Execution
```
POST /api/execute/tool
{
  "endpoint": "http://localhost:8000/mcp",
  "tool_name": "get_weather",
  "parameters": {"city": "San Francisco"},
  "api_key": "optional",
  "auth_header": "optional"
}
```

### Resource Access
```
POST /api/execute/resource
{
  "endpoint": "http://localhost:8000/mcp",
  "resource_uri": "file:///path/to/file",
  "api_key": "optional",
  "auth_header": "optional"
}
```

### Prompt Operations
```
POST /api/execute/prompt
{
  "endpoint": "http://localhost:8000/mcp",
  "prompt_name": "code_review",
  "parameters": {"language": "python"},
  "api_key": "optional",
  "auth_header": "optional"
}
```

## Terminal Commands

### Basic Commands
- `help` - Show available commands
- `clear` - Clear terminal output
- `status` - Show current configuration
- `endpoint <url>` - Set MCP endpoint
- `auth <api-key>` - Set API key authentication
- `auth header <header>` - Set custom auth header

### MCP Operations
- `discover [-v|-vv|-vvv] [--tool-tickle]` - Discover endpoint capabilities
- `tool <name> [json_params]` - Execute MCP tool with optional parameters
- `resource <uri>` - Read MCP resource
- `prompt <name> [json_params]` - Get MCP prompt with optional parameters

### Examples
```bash
# Set endpoint
endpoint http://localhost:8000/mcp

# Set authentication
auth sk-1234567890abcdef
# or
auth header Bearer eyJ0eXAiOiJKV1Q...

# Discover capabilities
discover -vv

# Execute tool
tool get_weather {"city": "New York", "units": "metric"}

# Read resource
resource file:///home/user/document.txt

# Get prompt
prompt code_review {"language": "python", "file": "main.py"}
```

## Styling & Theming

The interface uses a cyberpunk/hacker aesthetic inspired by Mr. Robot:

### Color Palette
- **Primary Green**: `#00ff00` - Main text and highlights
- **Secondary Green**: `#00cc00` - Secondary text and accents
- **Background Black**: `#000000` - Primary background
- **Terminal Green**: `#00ff0015` - Terminal transparency
- **Error Red**: `#ff0040` - Error messages
- **Info Blue**: `#0099ff` - Information text
- **Warning Yellow**: `#ffff00` - Warnings

### Typography
- **Primary Font**: Fira Code (monospace)
- **Secondary Font**: JetBrains Mono (monospace)
- **Font Sizes**: 12px-16px for terminal, 14px-24px for UI

### Effects
- **Matrix Rain**: Animated falling characters
- **Glitch Animation**: Periodic text distortion
- **Neon Glow**: Text shadow effects
- **Terminal Scan Lines**: CSS overlays for CRT effect
- **Cursor Blink**: Animated terminal cursor

## Development

### Project Structure
```
web/
├── backend/
│   └── app.py              # FastAPI server
├── frontend/
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Terminal.js
│   │   │   ├── MatrixRain.js
│   │   │   └── StatusBar.js
│   │   ├── App.js         # Main application
│   │   └── index.js       # React entry point
│   └── package.json       # Frontend dependencies
├── requirements.txt        # Backend dependencies
└── README.md              # This file
```

### Adding New Commands
1. Add command to `COMMANDS` object in `Terminal.js`
2. Add case handler in `executeCommand` function
3. Create corresponding API endpoint if needed
4. Update help text and documentation

### Styling Guidelines
- Use monospace fonts exclusively
- Maintain green-on-black color scheme
- Add subtle glow effects to important elements
- Use CSS animations sparingly for performance
- Ensure readability over flashy effects

## Deployment

### Development
```bash
# Terminal 1: Backend
cd web
python backend/app.py

# Terminal 2: Frontend
cd web/frontend
npm start
```

### Production
```bash
# Build frontend
cd web/frontend
npm run build

# Start backend (serves frontend automatically)
cd web
python backend/app.py
```

The backend serves the built React app at `http://localhost:8080`

## Security Considerations

- API keys are handled securely and never logged
- CORS is configured for development (restrict for production)
- Authentication headers are properly sanitized
- Error messages don't expose sensitive information
- Rate limiting should be added for production use

## Contributing

1. Follow the cyberpunk aesthetic guidelines
2. Maintain terminal-like interaction patterns
3. Use monospace fonts and green color scheme
4. Test both frontend and backend components
5. Update documentation for new features

## License

MIT License - Same as MCPeek main project