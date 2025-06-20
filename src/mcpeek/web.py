"""
MCPeek Web Interface Entry Point

Launches the web interface for MCPeek.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for mcpeek-web command."""
    # Get the web directory path
    mcpeek_root = Path(__file__).parent.parent.parent
    web_dir = mcpeek_root / "web"
    
    if not web_dir.exists():
        print("❌ Web interface not found. Please ensure the web directory exists.")
        sys.exit(1)
    
    # Change to web directory
    os.chdir(web_dir)
    
    # Check if start.sh exists and is executable
    start_script = web_dir / "start.sh"
    if start_script.exists():
        # Make executable if not already
        try:
            start_script.chmod(0o755)
            # Run the start script
            subprocess.run(["./start.sh"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start web interface: {e}")
            sys.exit(1)
    else:
        # Fallback to direct Python execution
        print("🚀 Starting MCPeek Web Interface...")
        try:
            subprocess.run([sys.executable, "backend/app.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start web interface: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()