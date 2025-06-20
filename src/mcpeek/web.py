"""Web interface entry point for MCPeek."""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Start the MCPeek web interface."""
    # Get the path to the web directory
    package_root = Path(__file__).parent.parent.parent
    web_dir = package_root / "web"
    
    if not web_dir.exists():
        print("❌ Web interface not found!")
        print(f"   Expected at: {web_dir}")
        print("   Please ensure the web directory exists with the interface files.")
        sys.exit(1)
    
    backend_dir = web_dir / "backend"
    app_file = backend_dir / "app.py"
    
    if not app_file.exists():
        print("❌ Web backend not found!")
        print(f"   Expected at: {app_file}")
        print("   Please ensure the web interface is properly installed.")
        sys.exit(1)
    
    print("🚀 Starting MCPeek Web Interface - Hacker Terminal Mode")
    print("=" * 55)
    print("🌐 Access at: http://localhost:8080")
    print("💀 Prepare for the most badass MCP exploration experience...")
    print()
    
    # Change to backend directory and run the app
    os.chdir(backend_dir)
    
    try:
        # Start the FastAPI backend
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 MCPeek Web Interface stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start web interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()