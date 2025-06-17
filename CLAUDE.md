# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Install with test dependencies
pip install -e .[test]
```

### Running the Application
```bash
# Run MCPeek directly
python -m mcpeek --help

# Or using the installed command
mcpeek --help

# Basic discovery example
mcpeek --discover http://localhost:8000/mcp

# Execute a tool
mcpeek http://localhost:8000/mcp --tool "tool_name" --input '{"param": "value"}'
```

### Code Quality and Testing
```bash
# Format code with Black
black src/

# Type checking with MyPy
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=mcpeek --cov-report=html

# Run specific test categories
pytest tests/test_transports.py
pytest tests/test_discovery.py
pytest tests/test_execution.py
```

## High-Level Architecture

MCPeek is a Python command-line tool for exploring and interacting with Model Context Protocol (MCP) endpoints. It follows a modular architecture with clean separation of concerns:

### Core Components

1. **CLI Interface** (`cli.py`) - Main command-line interface using argparse
2. **Configuration Management** (`config.py`) - Handles configuration from CLI args and environment variables
3. **Authentication** (`auth.py`) - Manages API keys and authentication headers
4. **MCP Client** (`mcp_client.py`) - Core MCP protocol implementation with JSON-RPC communication
5. **Discovery Engine** (`discovery.py`) - Explores endpoint capabilities with multiple verbosity levels
6. **Execution Engine** (`execution.py`) - Executes specific MCP operations (tools, resources, prompts)

### Transport Layer (`transports/`)
- **Base Transport** (`base.py`) - Abstract base class for all transports
- **HTTP Transport** (`http.py`) - HTTP/HTTPS implementation using aiohttp
- **STDIO Transport** (`stdio.py`) - Local subprocess communication for STDIO MCP servers

### Output System (`formatters/`)
- **Base Formatter** (`base.py`) - Abstract formatter interface
- **JSON Formatter** (`json.py`) - Structured JSON output for programmatic use
- **Table Formatter** (`table.py`) - Human-readable colorized tables using Rich

### Utilities (`utils/`)
- **Exceptions** (`exceptions.py`) - Custom exception hierarchy
- **Logging** (`logging.py`) - Centralized logging configuration
- **Helpers** (`helpers.py`) - Common utility functions

### Key Design Patterns

- **Async/Await**: All I/O operations use asyncio for non-blocking execution
- **Transport Abstraction**: Both HTTP and STDIO transports implement the same interface
- **Plugin Architecture**: Formatters and transports are easily extensible
- **Error Handling**: Comprehensive exception hierarchy with detailed error messages
- **Configuration Layering**: CLI args override environment variables

### Data Flow

1. CLI parses arguments and loads configuration
2. Authentication manager provides credentials
3. Transport layer (HTTP/STDIO) establishes connection
4. MCP Client performs protocol handshake and capability negotiation
5. Discovery Engine or Execution Engine performs requested operations
6. Output Formatter renders results in JSON or table format

### Authentication Strategy

- Environment variables: `MCPEEK_API_KEY`, `MCPEEK_<HOST>_KEY`
- CLI flags: `--api-key`, `--auth-header`
- Host-specific environment variables for multiple endpoints

### Testing Architecture

The project supports comprehensive testing with pytest:
- Unit tests for individual components
- Integration tests for component interactions
- Mock infrastructure for MCP servers
- Async test support with pytest-asyncio

## Project Configuration

- **Python Version**: 3.8+
- **Build System**: setuptools with pyproject.toml
- **Key Dependencies**: aiohttp (HTTP), rich (output), pydantic (validation)
- **Code Style**: Black with 100 character line length
- **Type Checking**: MyPy with strict configuration