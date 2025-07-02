#!/bin/bash

# MCPeek Web Interface Startup Script
# Badass hacker-themed terminal interface for MCP exploration

set -e

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${GREEN}"
echo "████████████████████████████████████████████████████████████████████████████████"
echo "██                                                                            ██"
echo "██  ███    ███  ██████ ██████  ███████ ███████ ██   ██                       ██"
echo "██  ████  ████ ██      ██   ██ ██      ██      ██  ██                        ██"
echo "██  ██ ████ ██ ██      ██████  █████   █████   █████                         ██"
echo "██  ██  ██  ██ ██      ██      ██      ██      ██  ██                        ██"
echo "██  ██      ██  ██████ ██      ███████ ███████ ██   ██                       ██"
echo "██                                                                            ██"
echo "██            🚀 WEB INTERFACE - HACKER TERMINAL MODE 🚀                     ██"
echo "██                                                                            ██"
echo "████████████████████████████████████████████████████████████████████████████████"
echo -e "${NC}"

echo -e "${CYAN}🚀 Starting MCPeek Web Interface...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check system requirements
echo -e "${BLUE}🔍 Checking system requirements...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION detected${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm $NPM_VERSION detected${NC}"
else
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi

# Environment configuration
echo -e "${BLUE}🔧 Loading environment configuration...${NC}"

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  No .env file found, copying from .env.example${NC}"
        echo -e "${YELLOW}   Please review and customize .env file for your environment${NC}"
    else
        # Create default .env file
        cat > .env << 'EOF'
# MCPeek Web Interface Configuration
MCPEEK_HOST=127.0.0.1
MCPEEK_PORT=8080
MCPEEK_LOG_LEVEL=INFO
MCPEEK_DEBUG=false
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
EOF
        echo -e "${YELLOW}⚠️  Created default .env file${NC}"
    fi
fi

# Load environment variables with defaults
export MCPEEK_HOST=${MCPEEK_HOST:-"127.0.0.1"}
export MCPEEK_PORT=${MCPEEK_PORT:-8080}
export MCPEEK_LOG_LEVEL=${MCPEEK_LOG_LEVEL:-"INFO"}
export MCPEEK_DEBUG=${MCPEEK_DEBUG:-"false"}
export MCPEEK_CORS_ORIGINS=${MCPEEK_CORS_ORIGINS:-"http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080"}

echo -e "${GREEN}✅ Environment configuration:${NC}"
echo -e "   Host: ${MCPEEK_HOST}"
echo -e "   Port: ${MCPEEK_PORT}"
echo -e "   Log Level: ${MCPEEK_LOG_LEVEL}"
echo -e "   Debug Mode: ${MCPEEK_DEBUG}"

# Install Python dependencies
echo -e "${BLUE}🔧 Installing Python dependencies...${NC}"
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn aiohttp rich pydantic
fi

# Install Node.js dependencies
echo -e "${BLUE}🔧 Installing Node.js dependencies...${NC}"
cd frontend
if [ -f package.json ]; then
    npm install
else
    echo -e "${RED}❌ frontend/package.json not found${NC}"
    exit 1
fi
cd ..

# Build frontend
echo -e "${BLUE}🔧 Building frontend...${NC}"
cd frontend
npm run build
cd ..

# Start backend in background
echo -e "${BLUE}🚀 Starting FastAPI backend...${NC}"
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${YELLOW}⏳ Waiting for backend to initialize...${NC}"
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend started successfully (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

# Display access information
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 MCPeek Web Interface is now running!${NC}"
echo ""
echo -e "${CYAN}🌐 Access the interface at:${NC}"
echo -e "   ${PURPLE}http://${MCPEEK_HOST}:${MCPEEK_PORT}${NC}"
echo ""
echo -e "${CYAN}🎮 Available Commands in Terminal:${NC}"
echo -e "   ${GREEN}endpoint <url>${NC}                 - Set MCP endpoint"
echo -e "   ${GREEN}discover [-v|-vv|-vvv]${NC}        - Explore capabilities"
echo -e "   ${GREEN}tool <name> [json-params]${NC}     - Execute MCP tools"
echo -e "   ${GREEN}resource <uri>${NC}                - Read MCP resources"
echo -e "   ${GREEN}prompt <name> [json-params]${NC}   - Get MCP prompts"
echo -e "   ${GREEN}auth <api-key>${NC}                - Set authentication"
echo -e "   ${GREEN}header <auth-header>${NC}          - Set custom headers"
echo -e "   ${GREEN}status${NC}                        - Show current settings"
echo -e "   ${GREEN}clear${NC}                         - Clear terminal"
echo -e "   ${GREEN}help${NC}                          - Toggle help panel"
echo ""
echo -e "${YELLOW}⚡ Press Ctrl+C to stop the interface${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Handle cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down MCPeek Web Interface...${NC}"
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    echo -e "${CYAN}👋 Thanks for using MCPeek Web Interface!${NC}"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait $BACKEND_PID