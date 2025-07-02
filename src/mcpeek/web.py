#!/usr/bin/env python3
"""
MCPeek Web Interface Entry Point
Launches the web interface startup script
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for the web interface"""
    # Find the web directory relative to this file
    current_dir = Path(__file__).parent
    web_dir = None
    
    # Try to find web directory starting from current location
    search_paths = [
        current_dir.parent.parent.parent / "web",  # From src/mcpeek/
        current_dir.parent.parent / "web",         # From src/
        current_dir.parent / "web",                # From mcpeek/
        Path.cwd() / "web",                        # From current working directory
    ]
    
    for path in search_paths:
        if path.exists() and (path / "start.sh").exists():
            web_dir = path
            break
    
    if not web_dir:
        print("❌ Error: Could not find web interface directory")
        print("   Make sure you're in the MCPeek repository root directory")
        print("   or that the web/ directory exists")
        sys.exit(1)
    
    # Make start.sh executable
    start_script = web_dir / "start.sh"
    try:
        os.chmod(start_script, 0o755)
    except:
        pass  # Ignore chmod errors on Windows
    
    print(f"🚀 Launching MCPeek Web Interface from: {web_dir}")
    
    try:
        # Execute the start script
        os.chdir(web_dir)
        if os.name == 'nt':  # Windows
            subprocess.run([str(start_script)], shell=True)
        else:  # Unix-like
            subprocess.run([str(start_script)])
    except KeyboardInterrupt:
        print("\n👋 MCPeek Web Interface stopped")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()