"""Main CLI interface for MCPeek."""

import argparse
import asyncio
import sys
from typing import List, Dict, Any

from .config import ConfigManager
from .auth import AuthManager
from .transports.http import HTTPTransport
from .transports.stdio import STDIOTransport
from .mcp_client import MCPClient
from .discovery import DiscoveryEngine
from .execution import ExecutionEngine
from .formatters.json import JSONFormatter
from .formatters.table import TableFormatter
from .utils.exceptions import MCPeekException, ValidationError, ConnectionError
from .utils.logging import logging_manager, get_logger
from .utils.helpers import parse_endpoint_url


class MCPeekCLI:
    """Main CLI interface using argparse."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
        self.logger = None  # Will be initialized after logging setup

    def setup_parser(self) -> argparse.ArgumentParser:
        """Configure command-line argument parser."""
        parser = argparse.ArgumentParser(
            prog="mcpeek",
            description="MCPeek - An elegant MCP (Model Context Protocol) exploration tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic discovery
  mcpeek --discover http://localhost:8000/mcp
  mcpeek --discover ./mcp-server

  # Discovery with verbosity levels
  mcpeek --discover <endpoint> -v          # Brief info
  mcpeek --discover <endpoint> -vv         # Detailed info
  mcpeek --discover <endpoint> -vvv        # Full schema info

  # Execute specific tools
  mcpeek --endpoint <endpoint> --tool <tool_name> --input '{"param": "value"}'
  mcpeek --endpoint <endpoint> --tool <tool_name> --stdin

  # Access resources
  mcpeek --endpoint <endpoint> --resource <resource_uri>

  # Output formatting
  mcpeek --discover <endpoint> --format json
  mcpeek --discover <endpoint> --format table

  # Authentication
  mcpeek --endpoint <endpoint> --api-key <key>
  mcpeek --endpoint <endpoint> --auth-header "Bearer <token>"
            """
        )

        # Main endpoint argument
        parser.add_argument(
            "endpoint",
            nargs="?",
            help="MCP endpoint URL (HTTP/HTTPS) or command (STDIO)"
        )

        # Discovery mode
        parser.add_argument(
            "--discover",
            action="store_true",
            help="Discover and catalog endpoint capabilities"
        )

        # Execution options
        parser.add_argument(
            "--tool",
            help="Execute a specific tool by name"
        )

        parser.add_argument(
            "--resource",
            help="Read a specific resource by URI"
        )

        parser.add_argument(
            "--prompt",
            help="Get a specific prompt by name"
        )

        # Input options
        parser.add_argument(
            "--input",
            help="Input data as JSON string or file path"
        )

        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Read input data from stdin"
        )

        # Output formatting
        parser.add_argument(
            "--format",
            choices=["json", "table"],
            default="table",
            help="Output format (default: table)"
        )

        # Verbosity levels
        parser.add_argument(
            "-v", "--verbose",
            action="count",
            default=0,
            dest="verbosity",
            help="Increase verbosity level (use -v, -vv, or -vvv)"
        )

        # Authentication
        parser.add_argument(
            "--api-key",
            help="API key for authentication"
        )

        parser.add_argument(
            "--auth-header",
            help="Custom authentication header (e.g., 'Bearer token')"
        )

        # Connection options
        parser.add_argument(
            "--timeout",
            type=float,
            default=30.0,
            help="Connection timeout in seconds (default: 30)"
        )

        # Logging
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Set logging level (default: INFO)"
        )

        return parser

    def parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse and validate command-line arguments."""
        parser = self.setup_parser()
        parsed_args = parser.parse_args(args)

        # Validate argument combinations
        self.validate_arguments(parsed_args)

        return parsed_args

    def validate_arguments(self, args: argparse.Namespace) -> None:
        """Validate argument combinations and requirements."""
        # Endpoint is required
        if not args.endpoint:
            raise ValidationError("Endpoint is required")

        # Must specify either discovery or execution mode
        execution_modes = [args.discover, args.tool, args.resource, args.prompt]
        if not any(execution_modes):
            raise ValidationError("Must specify either --discover, --tool, --resource, or --prompt")

        # Only one execution mode at a time
        if sum(bool(mode) for mode in execution_modes) > 1:
            raise ValidationError("Cannot specify multiple execution modes simultaneously")

        # Input validation
        if args.stdin and args.input:
            raise ValidationError("Cannot specify both --stdin and --input")

        # Tool/resource/prompt execution requires input in some cases
        if args.tool and not args.stdin and not args.input:
            # Tool execution without input is allowed (some tools don't need parameters)
            pass

        # Verbosity validation
        if args.verbosity > 3:
            raise ValidationError("Maximum verbosity level is 3 (-vvv)")

    async def execute_command(self, args: argparse.Namespace) -> int:
        """Execute the requested command and return exit code."""
        try:
            # Setup logging first
            logging_manager.setup_logging(args.log_level)
            self.logger = get_logger()

            # Load configuration
            config = self.config_manager.load_config(args)

            # Create transport and client
            transport = await self._create_transport(config)
            client = MCPClient(transport)

            try:
                # Execute the requested operation
                if config.get('discover'):
                    result = await self._execute_discovery(client, config)
                elif config.get('tool'):
                    result = await self._execute_tool(client, config)
                elif config.get('resource'):
                    result = await self._execute_resource(client, config)
                elif config.get('prompt'):
                    result = await self._execute_prompt(client, config)
                else:
                    raise ValidationError("No valid operation specified")

                # Format and output result
                formatter = self._create_formatter(config)
                if config.get('discover'):
                    output = formatter.format_discovery_result(result)
                elif config.get('tool'):
                    output = formatter.format_tool_result(result)
                elif config.get('resource'):
                    output = formatter.format_resource_result(result)
                elif config.get('prompt'):
                    output = formatter.format_tool_result(result)  # Prompts use same format as tools

                print(output)
                return 0

            finally:
                await client.close()

        except KeyboardInterrupt:
            if self.logger:
                self.logger.info("Operation cancelled by user")
            return 130
        except MCPeekException as e:
            if self.logger:
                self.logger.error(f"MCPeek error: {e}")
            else:
                print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error: {e}")
            else:
                print(f"Unexpected error: {e}", file=sys.stderr)
            return 1

    async def _create_transport(self, config: Dict[str, Any]):
        """Create appropriate transport based on endpoint."""
        endpoint = config['endpoint']
        endpoint_info = parse_endpoint_url(endpoint)

        # Get authentication headers
        auth_headers = self.auth_manager.get_auth_headers(
            endpoint,
            config.get('api_key'),
            config.get('auth_header')
        )

        timeout = config.get('timeout', 30.0)

        if endpoint_info['type'] == 'http':
            transport = HTTPTransport(endpoint, auth_headers, timeout)
        else:
            # STDIO transport
            if ' ' in endpoint:
                # Command with arguments
                transport = STDIOTransport.from_command_string(endpoint, timeout)
            else:
                # Simple executable
                transport = STDIOTransport([endpoint], timeout)

        await transport.connect()
        return transport

    async def _execute_discovery(self, client: MCPClient, config: Dict[str, Any]):
        """Execute discovery operation."""
        verbosity = config.get('verbosity', 0)
        discovery_engine = DiscoveryEngine(client, verbosity)
        return await discovery_engine.discover_endpoint()

    async def _execute_tool(self, client: MCPClient, config: Dict[str, Any]):
        """Execute tool operation."""
        execution_engine = ExecutionEngine(client)
        tool_name = config['tool']

        # Get input data
        input_data = None
        if config.get('stdin'):
            input_data = await execution_engine.handle_stdin_input()
        elif config.get('input'):
            input_data = execution_engine.process_input_data(config['input'])

        return await execution_engine.execute_tool(tool_name, input_data)

    async def _execute_resource(self, client: MCPClient, config: Dict[str, Any]):
        """Execute resource read operation."""
        execution_engine = ExecutionEngine(client)
        resource_uri = config['resource']
        return await execution_engine.read_resource(resource_uri)

    async def _execute_prompt(self, client: MCPClient, config: Dict[str, Any]):
        """Execute prompt get operation."""
        execution_engine = ExecutionEngine(client)
        prompt_name = config['prompt']

        # Get input data
        input_data = None
        if config.get('stdin'):
            input_data = await execution_engine.handle_stdin_input()
        elif config.get('input'):
            input_data = execution_engine.process_input_data(config['input'])

        return await execution_engine.get_prompt(prompt_name, input_data)

    def _create_formatter(self, config: Dict[str, Any]):
        """Create appropriate formatter based on config."""
        format_type = config.get('format', 'table')

        if format_type == 'json':
            return JSONFormatter(pretty_print=True)
        else:
            return TableFormatter(use_colors=True)