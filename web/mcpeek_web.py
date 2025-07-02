#!/usr/bin/env python3
"""
MCPeek Web Interface Entry Point
Badass hacker-themed MCP exploration interface
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Main entry point for mcpeek-web command."""
    
    # Get the web directory path
    web_dir = Path(__file__).parent
    
    print("🚀 Starting MCPeek Web Interface...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Change to web directory
    os.chdir(web_dir)
    
    # Check if start.sh exists
    start_script = web_dir / "start.sh"
    if start_script.exists():
        print("🔧 Using start.sh script...")
        try:
            # Make start.sh executable
            os.chmod(start_script, 0o755)
            # Run start.sh
            subprocess.run([str(start_script)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running start.sh: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down MCPeek Web Interface...")
            sys.exit(0)
    else:
        print("❌ start.sh not found in web directory")
        print(f"Expected location: {start_script}")
        sys.exit(1)


if __name__ == "__main__":
    main()