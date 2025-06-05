"""Main entry point for MCPeek."""

import sys
import asyncio
from .cli import MCPeekCLI


def main() -> int:
    """Main entry point for the MCPeek application."""
    try:
        cli = MCPeekCLI()
        args = cli.parse_arguments(sys.argv[1:])
        return asyncio.run(cli.execute_command(args))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())