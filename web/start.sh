#!/bin/bash

# MCPeek Web Interface Startup Script
# Badass hacker-themed terminal interface

set -e

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${GREEN}"
echo "🚀 Starting MCPeek Web Interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"

# Check system requirements
echo -e "${CYAN}🔍 Checking system requirements...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} detected${NC}"
else
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js ${NODE_VERSION} detected${NC}"
else
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm ${NPM_VERSION} detected${NC}"
else
    echo -e "${RED}❌ npm is required but not installed${NC}"
    exit 1
fi

# Environment configuration
echo -e "${CYAN}🔧 Loading environment configuration...${NC}"

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}⚠️  No .env file found, copying from .env.example${NC}"
        echo -e "${YELLOW}   Please review and customize .env file for your environment${NC}"
        cp .env.example .env
    else
        echo -e "${YELLOW}⚠️  No .env file found, creating default configuration${NC}"
        cat > .env << 'EOF'
# MCPeek Web Interface Configuration
MCPEEK_HOST=127.0.0.1
MCPEEK_PORT=8080
MCPEEK_LOG_LEVEL=INFO
MCPEEK_DEBUG=false
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080
EOF
    fi
fi

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}📄 Loading .env file...${NC}"
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Set default values
MCPEEK_HOST=${MCPEEK_HOST:-127.0.0.1}
MCPEEK_PORT=${MCPEEK_PORT:-8080}
MCPEEK_LOG_LEVEL=${MCPEEK_LOG_LEVEL:-INFO}
MCPEEK_DEBUG=${MCPEEK_DEBUG:-false}
MCPEEK_CORS_ORIGINS=${MCPEEK_CORS_ORIGINS:-"http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080"}

echo -e "${GREEN}✅ Environment configuration:${NC}"
echo -e "   Host: ${MCPEEK_HOST}"
echo -e "   Port: ${MCPEEK_PORT}"
echo -e "   Log Level: ${MCPEEK_LOG_LEVEL}"
echo -e "   Debug Mode: ${MCPEEK_DEBUG}"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📂 Working directory: ${SCRIPT_DIR}${NC}"

# Backend setup
echo -e "${PURPLE}🐍 Setting up Python backend...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${CYAN}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${CYAN}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${CYAN}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install backend dependencies
echo -e "${CYAN}📦 Installing backend dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Frontend setup
echo -e "${PURPLE}⚛️  Setting up React frontend...${NC}"

cd frontend

# Smart npm installation - use npm install if no package-lock.json exists
echo -e "${CYAN}📦 Installing frontend dependencies...${NC}"
if [ -f "package-lock.json" ]; then
    echo -e "${BLUE}📄 Found package-lock.json, using npm ci for faster installation${NC}"
    npm ci
else
    echo -e "${YELLOW}⚠️  No package-lock.json found, using npm install${NC}"
    npm install
fi

# Build frontend
echo -e "${CYAN}🔨 Building frontend...${NC}"
npm run build

cd ..

echo -e "${GREEN}✅ Frontend setup complete${NC}"

# Start services
echo -e "${PURPLE}🚀 Starting services...${NC}"

# Start backend in background
echo -e "${CYAN}🖥️  Starting backend server...${NC}"
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo -e "${CYAN}⏳ Waiting for backend to initialize...${NC}"
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✅ Backend server started successfully${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 MCPeek Web Interface is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${WHITE}💀 Access the badass hacker interface at: ${CYAN}http://${MCPEEK_HOST}:${MCPEEK_PORT}${WHITE} 💀${NC}"
echo -e "${GREEN}🎯 Matrix rain, terminal interface, and MCP exploration await!${NC}"
echo -e "${YELLOW}📋 Press Ctrl+C to stop the server${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Keep the script running and handle cleanup
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for backend process
wait $BACKEND_PID