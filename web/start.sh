#!/bin/bash

echo "🚀 Starting MCPeek Web Interface - Hacker Terminal Mode"
echo "=================================================="

# Check if running from web directory
if [ ! -f "start.sh" ]; then
    echo "❌ Please run this script from the web directory"
    echo "   cd web && ./start.sh"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
pip install -e ..

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js/npm is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Install and build React frontend
echo "🌐 Setting up React frontend..."
cd frontend
npm install

echo "🏗️  Building React app..."
npm run build

echo "🔙 Returning to web directory..."
cd ..

# Start the FastAPI backend (which will serve the built React app)
echo "🚀 Starting MCPeek Web Interface..."
echo ""
echo "🌟 Features:"
echo "   • Terminal-style hacker interface"
echo "   • Matrix rain background effect"
echo "   • Full MCPeek functionality"
echo "   • Command history and auto-completion"
echo "   • Real-time MCP operations"
echo ""
echo "🔗 Access the interface at: http://localhost:8080"
echo "💀 Prepare for the most badass MCP exploration experience..."
echo ""

# Start the backend server
cd backend
python app.py