# MCPeek Web GUI Interface

The MCPeek web interface has been transformed from a command-line style terminal to a modern point-and-click GUI while maintaining the hacker aesthetic.

## New Features

### 1. Tabbed Interface
The interface now features four main tabs:
- **Connect**: Configure endpoint connections
- **Tools**: Browse and execute MCP tools
- **Resources**: View available resources
- **Prompts**: Access MCP prompts

### 2. Connect Tab
- **Transport Type Selection**: Choose between HTTP/HTTPS or STDIO (local) connections via radio buttons
- **Endpoint Configuration**: Text input field for URLs or commands
- **Authentication**: Optional fields for API keys and custom auth headers
- **Discovery Button**: One-click endpoint discovery with loading animation

### 3. Tools Tab
- Displays all available tools as clickable cards
- Click a tool card to expand parameter input form
- Dynamic form generation based on tool requirements
- Execute button for each tool

### 4. Visual Enhancements
- Green glow effects on hover
- Smooth animations and transitions
- Matrix-style scanline effect
- Responsive form inputs with focus effects
- Loading spinners for async operations

### 5. Error Handling
- Clear error messages in red
- Success notifications in green
- Form validation

## Usage

1. Start the web interface:
   ```bash
   cd web
   ./start.sh
   ```

2. Open http://localhost:3000 in your browser

3. In the Connect tab:
   - Select transport type (HTTP or STDIO)
   - Enter endpoint URL or command
   - Add authentication if needed
   - Click "Discover Endpoint"

4. Navigate to other tabs to interact with discovered tools, resources, and prompts

## Design Highlights

- Maintains the Mr. Robot/Matrix aesthetic
- All interactive elements have hover effects
- Monospace font throughout for consistency
- Green-on-black color scheme preserved
- Smooth page transitions with Framer Motion