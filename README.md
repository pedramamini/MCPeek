# MCPeek

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An elegant MCP (Model Context Protocol) exploration tool written in Python 3. MCPeek is a "swiss army knife" for AI hackers to explore and interact with MCP endpoints, supporting both HTTP/S and STDIO transport mechanisms.

## 🚀 Features

- **Multi-Transport Support**: Works seamlessly with both HTTP/S and STDIO MCP endpoints
- **Discovery Mode**: Comprehensive endpoint exploration with `--discover`
- **Multiple Verbosity Levels**: Use `-v`, `-vv`, or `-vvv` for different detail levels
- **Tool Execution**: Call individual MCP functions with flexible parameter input
- **Resource Access**: Read MCP resources by URI with full content retrieval
- **Prompt Retrieval**: Access and execute MCP prompts with parameter support
- **Flexible Input Methods**: Support for JSON strings, file input, and stdin
- **Multiple Output Formats**: Beautiful table output and structured JSON formatting
- **Authentication**: Comprehensive auth support via API keys and custom headers
- **Environment Integration**: Smart environment variable handling
- **Comprehensive Logging**: Configurable logging levels with structured output
- **Error Handling**: Graceful error handling with detailed diagnostics

## 📦 Installation

### From PyPI

```bash
pip install mcpeek
```

### Development Installation

```bash
git clone https://github.com/mcpeek/mcpeek.git
cd mcpeek
pip install -e .
```

### With Development Dependencies

```bash
pip install -e .[dev]
```

### Requirements

- Python 3.8 or higher
- Core dependencies: `aiohttp`, `rich`, `pydantic`

## 🏃 Quick Start

### Basic Discovery

```bash
# Discover HTTP endpoint
mcpeek --discover http://localhost:8000/mcp

# Discover STDIO endpoint
mcpeek --discover ./mcp-server

# Discovery with verbosity levels
mcpeek --discover <endpoint> -v          # Brief info
mcpeek --discover <endpoint> -vv         # Detailed info
mcpeek --discover <endpoint> -vvv        # Full schema info
```

### Execute Tools

```bash
# Execute tool with JSON parameters
mcpeek <endpoint> --tool <tool_name> --input '{"param": "value"}'

# Execute tool with input from file
mcpeek <endpoint> --tool <tool_name> --input /path/to/input.json

# Execute tool with stdin input
echo '{"param": "value"}' | mcpeek <endpoint> --tool <tool_name> --stdin
```

### Access Resources

```bash
# Read a resource
mcpeek <endpoint> --resource <resource_uri>
```

### Get Prompts

```bash
# Get a prompt with parameters
mcpeek <endpoint> --prompt <prompt_name> --input '{"param": "value"}'
```

## 📖 Detailed Usage

### Discovery Mode

Discovery mode provides comprehensive exploration of MCP endpoint capabilities:

#### Basic Discovery
```bash
mcpeek --discover http://localhost:8000/mcp
```

#### Verbosity Levels

**Level 1 (`-v`)**: Brief overview
- Tool names and descriptions
- Resource URIs and basic info
- Prompt names

```bash
mcpeek --discover http://localhost:8000/mcp -v
```

**Level 2 (`-vv`)**: Detailed information
- Parameter names and types
- Required vs optional fields
- Resource metadata

```bash
mcpeek --discover http://localhost:8000/mcp -vv
```

**Level 3 (`-vvv`)**: Full schema details
- Complete JSON schemas
- Parameter examples
- Full capability information

```bash
mcpeek --discover http://localhost:8000/mcp -vvv
```

### Tool Execution

MCPeek supports flexible tool execution with various input methods:

#### JSON String Input
```bash
mcpeek http://localhost:8000/mcp --tool "get_weather" --input '{"city": "San Francisco", "units": "metric"}'
```

#### File Input
```bash
# Create input file
echo '{"city": "San Francisco", "units": "metric"}' > weather_input.json

# Execute tool with file input
mcpeek http://localhost:8000/mcp --tool "get_weather" --input weather_input.json
```

#### Stdin Input
```bash
# Pipe input directly
echo '{"city": "San Francisco"}' | mcpeek http://localhost:8000/mcp --tool "get_weather" --stdin

# From file via stdin
cat weather_input.json | mcpeek http://localhost:8000/mcp --tool "get_weather" --stdin
```

#### Tools Without Parameters
```bash
# Some tools don't require input parameters
mcpeek http://localhost:8000/mcp --tool "list_available_models"
```

### Resource Access

Access MCP resources by their URI:

```bash
# Read a specific resource
mcpeek http://localhost:8000/mcp --resource "file:///path/to/document.txt"

# Access web resources
mcpeek http://localhost:8000/mcp --resource "https://api.example.com/data"

# Custom resource schemes
mcpeek http://localhost:8000/mcp --resource "custom://resource/identifier"
```

### Prompt Operations

Retrieve and execute prompts with parameters:

```bash
# Get prompt with parameters
mcpeek http://localhost:8000/mcp --prompt "code_review" --input '{"language": "python", "file": "main.py"}'

# Get prompt from file input
mcpeek http://localhost:8000/mcp --prompt "analysis" --input prompt_params.json

# Get prompt via stdin
echo '{"topic": "machine learning"}' | mcpeek http://localhost:8000/mcp --prompt "explain_topic" --stdin
```

## 🔧 Output Formats

### Table Format (Default)

Beautiful, colorized table output perfect for human consumption:

```bash
mcpeek --discover http://localhost:8000/mcp --format table
```

Features:
- Syntax highlighting
- Organized sections for tools, resources, and prompts
- Color-coded parameter types
- Clear visual hierarchy

### JSON Format

Structured JSON output ideal for programmatic use:

```bash
mcpeek --discover http://localhost:8000/mcp --format json
```

Features:
- Pretty-printed JSON
- Complete schema information
- Machine-readable format
- Suitable for piping to other tools

## 🔐 Authentication

MCPeek provides flexible authentication options for secure endpoint access:

### Environment Variables

Set default authentication:
```bash
export MCPEEK_API_KEY="your-api-key"
mcpeek --discover http://localhost:8000/mcp
```

### Endpoint-Specific Environment Variables

For multiple endpoints with different credentials:
```bash
# For api.example.com
export MCPEEK_API_EXAMPLE_COM_KEY="your-api-key"

# For internal.company.com
export MCPEEK_INTERNAL_COMPANY_COM_KEY="internal-key"
```

### Command Line Authentication

#### API Key
```bash
mcpeek --discover http://localhost:8000/mcp --api-key "your-api-key"
```

#### Custom Auth Header
```bash
# Bearer token
mcpeek --discover http://localhost:8000/mcp --auth-header "Bearer your-jwt-token"

# Custom header format
mcpeek --discover http://localhost:8000/mcp --auth-header "X-API-Key your-api-key"
```

## ⚙️ Configuration

### Command Line Options

```
usage: mcpeek [-h] [--discover] [--tool TOOL] [--resource RESOURCE]
              [--prompt PROMPT] [--input INPUT] [--stdin]
              [--format {json,table}] [-v] [--api-key API_KEY]
              [--auth-header AUTH_HEADER] [--timeout TIMEOUT]
              [--log-level {DEBUG,INFO,WARNING,ERROR}]
              [endpoint]

MCPeek - An elegant MCP (Model Context Protocol) exploration tool

positional arguments:
  endpoint              MCP endpoint URL (HTTP/HTTPS) or command (STDIO)

options:
  -h, --help            show this help message and exit
  --discover            Discover and catalog endpoint capabilities
  --tool TOOL           Execute a specific tool by name
  --resource RESOURCE   Read a specific resource by URI
  --prompt PROMPT       Get a specific prompt by name
  --input INPUT         Input data as JSON string or file path
  --stdin               Read input data from stdin
  --format {json,table} Output format (default: table)
  -v, --verbose         Increase verbosity level (use -v, -vv, or -vvv)
  --api-key API_KEY     API key for authentication
  --auth-header AUTH_HEADER
                        Custom authentication header (e.g., 'Bearer token')
  --timeout TIMEOUT     Connection timeout in seconds (default: 30)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Set logging level (default: INFO)
```

### Environment Variables

MCPeek supports the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `MCPEEK_API_KEY` | Default API key for authentication | `your-default-api-key` |
| `MCPEEK_ENDPOINT` | Default endpoint URL | `http://localhost:8000/mcp` |
| `MCPEEK_FORMAT` | Default output format | `json` or `table` |
| `MCPEEK_TIMEOUT` | Default connection timeout | `30` |
| `MCPEEK_LOG_LEVEL` | Default logging level | `INFO` |
| `MCPEEK_<HOST>_KEY` | Host-specific API key | `MCPEEK_API_EXAMPLE_COM_KEY` |

## 📚 Examples

### Comprehensive Discovery Workflow

```bash
# Start with basic discovery
mcpeek --discover http://localhost:8000/mcp

# Get detailed information about capabilities
mcpeek --discover http://localhost:8000/mcp -vv

# Export full schema for documentation
mcpeek --discover http://localhost:8000/mcp -vvv --format json > mcp_schema.json
```

### Tool Execution Workflow

```bash
# Discover available tools first
mcpeek --discover http://localhost:8000/mcp -v

# Execute a simple tool
mcpeek http://localhost:8000/mcp --tool "get_system_info"

# Execute tool with parameters
mcpeek http://localhost:8000/mcp --tool "search_files" --input '{"pattern": "*.py", "directory": "/src"}'

# Chain operations with JSON output
mcpeek http://localhost:8000/mcp --tool "list_databases" --format json | \
  jq '.result.databases[0].name' | \
  xargs -I {} mcpeek http://localhost:8000/mcp --tool "query_database" --input "{\"db_name\": \"{}\"}"
```

### STDIO Transport Examples

```bash
# Simple executable
mcpeek --discover ./mcp-server

# Executable with arguments
mcpeek --discover "python mcp_server.py --port 8080"

# Complex command with environment
mcpeek --discover "env NODE_ENV=production node server.js"

# Tool execution via STDIO
mcpeek ./mcp-server --tool "list_files" --input '{"directory": "/tmp"}'
```

### Authentication Examples

```bash
# Multiple endpoints with different auth
export MCPEEK_API_OPENAI_COM_KEY="sk-..."
export MCPEEK_API_ANTHROPIC_COM_KEY="ant-..."

mcpeek --discover https://api.openai.com/mcp
mcpeek --discover https://api.anthropic.com/mcp

# Custom authentication headers
mcpeek --discover https://internal-api.company.com/mcp \
  --auth-header "X-Internal-Token: $(cat ~/.company-token)"
```

### Advanced Usage Patterns

```bash
# Batch resource processing
for uri in $(mcpeek http://localhost:8000/mcp --discover -v | grep "Resource:" | cut -d' ' -f2); do
  echo "Processing $uri"
  mcpeek http://localhost:8000/mcp --resource "$uri" --format json > "resource_$(basename $uri).json"
done

# Interactive tool testing
while read -p "Tool name: " tool; do
  read -p "Parameters (JSON): " params
  mcpeek http://localhost:8000/mcp --tool "$tool" --input "$params"
done

# Monitoring endpoint health
watch -n 30 'mcpeek --discover http://localhost:8000/mcp --log-level ERROR'
```

## 🏗️ Architecture

MCPeek follows a modular architecture with clean separation of concerns:

### Core Components

- **Transport Layer**: HTTP and STDIO implementations for endpoint communication
- **MCP Client**: Core protocol implementation handling JSON-RPC communication
- **Discovery Engine**: Comprehensive endpoint capability exploration
- **Execution Engine**: Tool, resource, and prompt operation handling
- **Output Formatters**: JSON and table formatting with rich visual output
- **Authentication Manager**: Secure credential handling and header management
- **Configuration Manager**: Multi-source configuration with environment integration

### Transport Support

#### HTTP/HTTPS Transport
- Full HTTP/1.1 and HTTP/2 support via `aiohttp`
- SSL/TLS certificate validation
- Connection pooling and keep-alive
- Timeout and retry handling
- Custom header support

#### STDIO Transport
- Subprocess management for local MCP servers
- Non-blocking I/O for real-time communication
- Command-line argument parsing
- Environment variable passing
- Graceful process lifecycle management

## 🔍 Error Handling

MCPeek provides comprehensive error handling with detailed diagnostics:

### Error Categories

- **Connection Errors**: Network issues, timeouts, unreachable endpoints
- **Authentication Errors**: Invalid credentials, expired tokens
- **Protocol Errors**: MCP specification violations, malformed messages
- **Validation Errors**: Invalid input parameters, schema mismatches
- **Runtime Errors**: Tool execution failures, resource access issues

### Debugging

Enable debug logging for detailed troubleshooting:

```bash
# Debug mode with full protocol logging
mcpeek --discover http://localhost:8000/mcp --log-level DEBUG

# Capture debug output to file
mcpeek --discover http://localhost:8000/mcp --log-level DEBUG 2> debug.log

# Verbose discovery with debug logging
mcpeek --discover http://localhost:8000/mcp -vvv --log-level DEBUG
```

### Common Issues and Solutions

#### Connection Issues
```bash
# Test basic connectivity
mcpeek --discover http://localhost:8000/mcp --timeout 5

# Check with different transport
mcpeek --discover ./local-mcp-server --log-level DEBUG
```

#### Authentication Issues
```bash
# Verify API key
echo $MCPEEK_API_KEY

# Test with explicit auth
mcpeek --discover http://localhost:8000/mcp --api-key "test-key" --log-level DEBUG
```

#### Protocol Issues
```bash
# Check server capabilities
mcpeek --discover http://localhost:8000/mcp -vvv --format json | jq '.capabilities'

# Validate tool parameters
mcpeek --discover http://localhost:8000/mcp -vv | grep -A 10 "tool_name"
```

## 🧪 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/mcpeek/mcpeek.git
cd mcpeek

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcpeek --cov-report=html

# Run specific test categories
pytest tests/test_transports.py
pytest tests/test_discovery.py
pytest tests/test_execution.py
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Lint code
flake8 src/

# Run all quality checks
make quality  # If Makefile is available
```

### Project Structure

```
mcpeek/
├── src/mcpeek/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── auth.py              # Authentication handling
│   ├── mcp_client.py        # Core MCP client
│   ├── discovery.py         # Discovery engine
│   ├── execution.py         # Execution engine
│   ├── transports/          # Transport implementations
│   │   ├── base.py          # Abstract transport base
│   │   ├── http.py          # HTTP/HTTPS transport
│   │   └── stdio.py         # STDIO transport
│   ├── formatters/          # Output formatters
│   │   ├── base.py          # Abstract formatter base
│   │   ├── json.py          # JSON formatter
│   │   └── table.py         # Table formatter
│   └── utils/               # Utility modules
│       ├── exceptions.py    # Custom exceptions
│       ├── logging.py       # Logging configuration
│       └── helpers.py       # Helper functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 🤝 Contributing

We welcome contributions to MCPeek! Here's how to get started:

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Make your changes** with appropriate tests
3. **Ensure code quality** by running the test suite and linters
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest
black src/
mypy src/

# Commit changes
git commit -m "Add your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

### Reporting Issues

When reporting issues, please include:

- MCPeek version (`mcpeek --version`)
- Python version
- Operating system
- Complete command that failed
- Full error output with `--log-level DEBUG`
- Expected vs actual behavior

## 📄 License

MCPeek is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/) specification
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Powered by [aiohttp](https://github.com/aio-libs/aiohttp) for async HTTP operations
- Type safety with [Pydantic](https://github.com/pydantic/pydantic)

## 📞 Support

- **Documentation**: [https://mcpeek.readthedocs.io](https://mcpeek.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/mcpeek/mcpeek/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mcpeek/mcpeek/discussions)
- **Security**: Report security issues to security@mcpeek.com

---

**MCPeek** - Explore the Model Context Protocol with elegance and power.