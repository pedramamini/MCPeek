#!/bin/bash

# MCPeek Web Interface Startup Script
# Creates a badass hacker-themed terminal interface

set -e

# Make this script executable if it isn't already
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

echo "🚀 Starting MCPeek Web Interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
echo "🔍 Checking system requirements..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | sed 's/Python //')
    echo "✅ Python $PYTHON_VERSION detected"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi

if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION detected"
else
    echo "❌ Node.js not found. Please install Node.js 16 or later."
    exit 1
fi

if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION detected"
else
    echo "❌ npm not found. Please install npm."
    exit 1
fi

# Load environment configuration
echo "🔧 Loading environment configuration..."
if [ ! -f .env ]; then
    echo "⚠️  No .env file found, copying from .env.example"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "   Please review and customize .env file for your environment"
    else
        # Create default .env file
        cat > .env << 'EOF'
# MCPeek Web Interface Configuration
MCPEEK_WEB_HOST=127.0.0.1
MCPEEK_WEB_PORT=8080
MCPEEK_LOG_LEVEL=INFO
MCPEEK_DEBUG=false
MCPEEK_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
EOF
        echo "   Created default .env file"
    fi
fi

# Source environment variables
source .env

# Set defaults if not specified
export MCPEEK_WEB_HOST=${MCPEEK_WEB_HOST:-127.0.0.1}
export MCPEEK_WEB_PORT=${MCPEEK_WEB_PORT:-8080}
export MCPEEK_LOG_LEVEL=${MCPEEK_LOG_LEVEL:-INFO}
export MCPEEK_DEBUG=${MCPEEK_DEBUG:-false}
export MCPEEK_CORS_ORIGINS=${MCPEEK_CORS_ORIGINS:-"http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080"}

echo "✅ Environment configuration:"
echo "   Host: $MCPEEK_WEB_HOST"
echo "   Port: $MCPEEK_WEB_PORT"
echo "   Log Level: $MCPEEK_LOG_LEVEL"
echo "   Debug Mode: $MCPEEK_DEBUG"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt not found in web directory"
    exit 1
fi

pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend

if [ ! -f package.json ]; then
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

# Use npm install instead of npm ci for initial setup
if [ ! -f package-lock.json ]; then
    echo "📦 No package-lock.json found, running npm install..."
    npm install
else
    echo "📦 Using existing package-lock.json, running npm ci..."
    npm ci
fi

# Build frontend
echo "🔨 Building frontend..."
npm run build

cd ..

# Start the backend server
echo "🚀 Starting MCPeek Web Interface..."
echo "   Access at: http://$MCPEEK_WEB_HOST:$MCPEEK_WEB_PORT"
echo "   Press Ctrl+C to stop"
echo ""

cd backend
python app.py