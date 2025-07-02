#!/usr/bin/env python3
"""
MCPeek Web Interface Launcher
Entry point for launching the web interface
"""

import os
import sys
import importlib.util
from pathlib import Path

def main():
    """Main entry point for mcpeek-web command"""
    # Get the directory where this script is located
    web_dir = Path(__file__).parent
    launcher_script = web_dir / "mcpeek-web"
    
    if not launcher_script.exists():
        print(f"❌ Web interface launcher not found: {launcher_script}")
        sys.exit(1)
    
    # Load and execute the launcher script
    spec = importlib.util.spec_from_file_location("mcpeek_web_launcher", launcher_script)
    if spec and spec.loader:
        launcher_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(launcher_module)
        if hasattr(launcher_module, 'main'):
            launcher_module.main()
        else:
            print("❌ Launcher script missing main() function")
            sys.exit(1)
    else:
        print("❌ Could not load launcher script")
        sys.exit(1)

if __name__ == "__main__":
    main()