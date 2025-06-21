#!/bin/bash

# MCPeek Web Interface Startup Script
# Enhanced version with error handling, security checks, and configuration validation

set -euo pipefail  # Exit on error, undefined vars, pipe failures

echo "🚀 Starting MCPeek Web Interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check requirements
check_requirements() {
    echo "🔍 Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        echo "   Please install Python 3.8 or higher"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo "✅ Python $PYTHON_VERSION detected"
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed."
        echo "   Please install Node.js 16 or higher"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION detected"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is required but not installed."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION detected"
}

# Function to load environment configuration
load_environment() {
    echo "🔧 Loading environment configuration..."
    
    if [ -f ".env" ]; then
        echo "📄 Loading .env file..."
        set -a  # Export all variables
        source .env
        set +a  # Stop exporting
    elif [ -f ".env.example" ]; then
        echo "⚠️  No .env file found, copying from .env.example"
        cp .env.example .env
        echo "   Please review and customize .env file for your environment"
    else
        echo "ℹ️  Using default environment configuration"
    fi
    
    # Set default values if not provided
    export MCPEEK_API_HOST=${MCPEEK_API_HOST:-"127.0.0.1"}
    export MCPEEK_API_PORT=${MCPEEK_API_PORT:-"8080"}
    export MCPEEK_LOG_LEVEL=${MCPEEK_LOG_LEVEL:-"INFO"}
    export MCPEEK_DEBUG=${MCPEEK_DEBUG:-"false"}
}

# Function to validate configuration
validate_configuration() {
    echo "✅ Environment configuration:"
    echo "   Host: $MCPEEK_API_HOST"
    echo "   Port: $MCPEEK_API_PORT"
    echo "   Log Level: $MCPEEK_LOG_LEVEL"
    echo "   Debug Mode: $MCPEEK_DEBUG"
    
    # Warn about security settings
    if [ "$MCPEEK_DEBUG" = "true" ]; then
        echo "⚠️  WARNING: Debug mode is enabled - do not use in production!"
    fi
    
    if [[ "$MCPEEK_CORS_ORIGINS" == *"*"* ]]; then
        echo "⚠️  WARNING: CORS allows all origins - configure properly for production!"
    fi
}

check_requirements
load_environment
validate_configuration

# Get the directory of this script and navigate to it
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
echo "📂 Working directory: $SCRIPT_DIR"

# Setup Python virtual environment
setup_backend() {
    echo "🐍 Setting up Python backend..."
    
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment"
            exit 1
        fi
    fi
    
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    
    echo "📦 Upgrading pip..."
    pip install --upgrade pip
    
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install backend dependencies"
        exit 1
    fi
    
    echo "✅ Backend setup complete"
}

setup_backend

# Setup frontend
setup_frontend() {
    echo "⚛️  Setting up React frontend..."
    
    cd frontend
    
    if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm ci  # Use ci for faster, reliable installs
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install frontend dependencies"
            exit 1
        fi
    else
        echo "✅ Frontend dependencies already installed"
    fi
    
    # Run tests in CI mode
    if [ "${MCPEEK_SKIP_TESTS:-false}" != "true" ]; then
        echo "🧪 Running frontend tests..."
        npm run test:ci
        if [ $? -ne 0 ]; then
            echo "❌ Frontend tests failed"
            exit 1
        fi
    fi
    
    # Build frontend for production
    echo "🔨 Building frontend..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Frontend build failed"
        exit 1
    fi
    
    cd ..
    echo "✅ Frontend setup complete"
}

setup_frontend

# Function to display startup information
show_startup_info() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 MCPeek Web Interface is starting..."
    echo "🌐 Backend API: http://$MCPEEK_API_HOST:$MCPEEK_API_PORT/api"
    echo "🖥️  Web Interface: http://$MCPEEK_API_HOST:$MCPEEK_API_PORT"
    echo "📊 Health Check: http://$MCPEEK_API_HOST:$MCPEEK_API_PORT/api/health"
    
    if [ "$MCPEEK_DEBUG" = "true" ]; then
        echo "📚 API Docs: http://$MCPEEK_API_HOST:$MCPEEK_API_PORT/docs"
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "💡 Terminal Commands:"
    echo "   help                     - Show available commands"
    echo "   endpoint <url>           - Set MCP endpoint"
    echo "   discover [-v|-vv|-vvv]   - Explore endpoint capabilities"
    echo "   tool <name> [params]     - Execute MCP tool"
    echo "   resource <uri>           - Read MCP resource"
    echo "   prompt <name> [params]   - Get MCP prompt"
    echo "   status                   - Show current configuration"
    echo "   clear                    - Clear terminal"
    echo ""
    echo "🔐 Authentication:"
    echo "   auth <api-key>           - Set API key"
    echo "   auth header <header>     - Set custom auth header"
    echo ""
    echo "🔧 Configuration:"
    echo "   Environment file: ${PWD}/.env"
    echo "   Backend logs: Check terminal output"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down MCPeek Web Interface..."
    echo "✅ Cleanup complete. Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

show_startup_info

# Start the backend server with proper error handling
start_server() {
    echo "🚀 Starting backend server..."
    echo "   Host: $MCPEEK_API_HOST"
    echo "   Port: $MCPEEK_API_PORT"
    echo ""
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run backend tests if not skipped
    if [ "${MCPEEK_SKIP_TESTS:-false}" != "true" ]; then
        echo "🧪 Running backend tests..."
        python -m pytest tests/ -v
        if [ $? -ne 0 ]; then
            echo "❌ Backend tests failed"
            exit 1
        fi
        echo "✅ Backend tests passed"
        echo ""
    fi
    
    # Start the server
    python backend/app.py
}

start_server