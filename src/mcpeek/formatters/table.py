"""Human-readable table formatting using rich."""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import box
import io

from .base import BaseFormatter, DiscoveryResult
from ..utils.helpers import extract_error_details, safe_json_dumps


class TableFormatter(BaseFormatter):
    """Human-readable table formatting."""

    def __init__(self, use_colors: bool = True):
        """Initialize table formatter with color option."""
        super().__init__()
        self.console = Console(color_system="auto" if use_colors else None, width=120)

    def format_discovery_result(self, result: DiscoveryResult) -> str:
        """Format discovery results as colorized tables using rich."""
        output = io.StringIO()
        console = Console(file=output, width=120)

        # Server Information Panel
        server_panel = self._create_server_info_panel(result.server_info, result.capabilities)
        console.print(server_panel)
        console.print()

        # Summary
        summary_text = f"[bold green]Discovery Summary[/bold green]\n"
        summary_text += f"Tools: {len(result.tools)} | Resources: {len(result.resources)} | Prompts: {len(result.prompts)}"
        console.print(Panel(summary_text, title="Summary", border_style="green"))
        console.print()

        # Tools Table
        if result.tools:
            tools_table = self._create_tools_table(result.tools, result.verbosity_level)
            console.print(Panel(tools_table, title="Available Tools", border_style="blue"))
            console.print()

        # Resources Table
        if result.resources:
            resources_table = self._create_resources_table(result.resources, result.verbosity_level)
            console.print(Panel(resources_table, title="Available Resources", border_style="yellow"))
            console.print()

        # Prompts Table
        if result.prompts:
            prompts_table = self._create_prompts_table(result.prompts, result.verbosity_level)
            console.print(Panel(prompts_table, title="Available Prompts", border_style="magenta"))

        return output.getvalue()

    def format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool execution results as structured tables."""
        output = io.StringIO()
        console = Console(file=output, width=120)

        # Tool execution result
        if "result" in result:
            tool_result = result["result"]
            if isinstance(tool_result, dict):
                table = self._create_dict_table(tool_result, "Tool Result")
                console.print(table)
            elif isinstance(tool_result, list):
                table = self._create_list_table(tool_result, "Tool Result")
                console.print(table)
            else:
                console.print(Panel(str(tool_result), title="Tool Result", border_style="green"))
        else:
            # Show full result
            table = self._create_dict_table(result, "Tool Execution")
            console.print(table)

        return output.getvalue()

    def format_resource_result(self, result: Dict[str, Any]) -> str:
        """Format resource read results as structured tables."""
        output = io.StringIO()
        console = Console(file=output, width=120)

        if "contents" in result:
            contents = result["contents"]
            if isinstance(contents, list) and contents:
                # Multiple content items
                for i, content in enumerate(contents):
                    title = f"Resource Content {i+1}"
                    if "uri" in content:
                        title += f" ({content['uri']})"

                    content_panel = self._create_content_panel(content)
                    console.print(Panel(content_panel, title=title, border_style="cyan"))
                    if i < len(contents) - 1:
                        console.print()
            else:
                # Single content or empty
                content_panel = self._create_content_panel(contents[0] if contents else {})
                console.print(Panel(content_panel, title="Resource Content", border_style="cyan"))
        else:
            # Show full result
            table = self._create_dict_table(result, "Resource Result")
            console.print(table)

        return output.getvalue()

    def format_error(self, error: Exception) -> str:
        """Format error messages with rich styling."""
        output = io.StringIO()
        console = Console(file=output, width=120)

        error_details = extract_error_details(error)

        error_text = f"[bold red]{error_details['type']}[/bold red]\n"
        error_text += f"[red]{error_details['message']}[/red]"

        if error_details.get('details'):
            error_text += f"\n\n[dim]Details:[/dim]\n{safe_json_dumps(error_details['details'], pretty=True)}"

        console.print(Panel(error_text, title="Error", border_style="red"))
        return output.getvalue()

    def _create_server_info_panel(self, server_info: Dict[str, Any], capabilities: Dict[str, Any]) -> Panel:
        """Create server information panel."""
        info_text = ""

        if server_info:
            info_text += "[bold]Server Information[/bold]\n"
            for key, value in server_info.items():
                info_text += f"  {key}: {value}\n"
            info_text += "\n"

        if capabilities:
            info_text += "[bold]Capabilities[/bold]\n"
            for key, value in capabilities.items():
                info_text += f"  {key}: {value}\n"

        return Panel(info_text.strip(), title="Server Info", border_style="blue")

    def _create_tools_table(self, tools: List, verbosity: int) -> Table:
        """Create tools table based on verbosity level."""
        table = Table(box=box.ROUNDED)

        # Add columns based on verbosity
        table.add_column("Name", style="bold blue")

        if verbosity >= 1:
            table.add_column("Description", style="dim")

        if verbosity >= 2:
            table.add_column("Parameters", style="green")

        if verbosity >= 3:
            table.add_column("Schema", style="yellow")

        # Add rows
        for tool in tools:
            row = [tool.name]

            if verbosity >= 1:
                desc = tool.description or "No description"
                row.append(self.truncate_text(desc, 50))

            if verbosity >= 2:
                params = self.format_parameter_info(tool.parameters, verbosity)
                row.append(self.truncate_text(params, 40))

            if verbosity >= 3:
                schema = safe_json_dumps(tool.schema, pretty=False) if tool.schema else "None"
                row.append(self.truncate_text(schema, 60))

            table.add_row(*row)

        return table

    def _create_resources_table(self, resources: List, verbosity: int) -> Table:
        """Create resources table based on verbosity level."""
        table = Table(box=box.ROUNDED)

        table.add_column("URI", style="bold cyan")

        if verbosity >= 1:
            table.add_column("Name", style="blue")
            table.add_column("Description", style="dim")

        if verbosity >= 2:
            table.add_column("MIME Type", style="green")

        if verbosity >= 3:
            table.add_column("Metadata", style="yellow")

        for resource in resources:
            row = [resource.uri]

            if verbosity >= 1:
                row.append(resource.name or "")
                desc = resource.description or "No description"
                row.append(self.truncate_text(desc, 50))

            if verbosity >= 2:
                row.append(resource.mime_type or "unknown")

            if verbosity >= 3:
                metadata = safe_json_dumps(resource.metadata, pretty=False) if resource.metadata else "None"
                row.append(self.truncate_text(metadata, 60))

            table.add_row(*row)

        return table

    def _create_prompts_table(self, prompts: List, verbosity: int) -> Table:
        """Create prompts table based on verbosity level."""
        table = Table(box=box.ROUNDED)

        table.add_column("Name", style="bold magenta")

        if verbosity >= 1:
            table.add_column("Description", style="dim")

        if verbosity >= 2:
            table.add_column("Parameters", style="green")

        if verbosity >= 3:
            table.add_column("Schema", style="yellow")

        for prompt in prompts:
            row = [prompt.name]

            if verbosity >= 1:
                desc = prompt.description or "No description"
                row.append(self.truncate_text(desc, 50))

            if verbosity >= 2:
                params = self.format_parameter_info(prompt.parameters, verbosity)
                row.append(self.truncate_text(params, 40))

            if verbosity >= 3:
                schema = safe_json_dumps(prompt.schema, pretty=False) if prompt.schema else "None"
                row.append(self.truncate_text(schema, 60))

            table.add_row(*row)

        return table

    def _create_dict_table(self, data: Dict[str, Any], title: str) -> Table:
        """Create a table from dictionary data."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Key", style="bold blue")
        table.add_column("Value", style="green")

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value_str = safe_json_dumps(value, pretty=True)
            else:
                value_str = str(value)

            table.add_row(key, self.truncate_text(value_str, 80))

        return table

    def _create_list_table(self, data: List[Any], title: str) -> Table:
        """Create a table from list data."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Index", style="bold blue")
        table.add_column("Value", style="green")

        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                item_str = safe_json_dumps(item, pretty=True)
            else:
                item_str = str(item)

            table.add_row(str(i), self.truncate_text(item_str, 80))

        return table

    def _create_content_panel(self, content: Dict[str, Any]) -> str:
        """Create content panel for resource content."""
        if not content:
            return "[dim]No content[/dim]"

        content_text = ""

        if "mimeType" in content:
            content_text += f"[bold]MIME Type:[/bold] {content['mimeType']}\n"

        if "uri" in content:
            content_text += f"[bold]URI:[/bold] {content['uri']}\n"

        if "text" in content:
            text_content = content["text"]
            if len(text_content) > 500:
                text_content = text_content[:500] + "..."
            content_text += f"\n[bold]Content:[/bold]\n{text_content}"
        elif "blob" in content:
            content_text += f"\n[bold]Binary Content:[/bold] {len(content['blob'])} bytes"

        return content_text.strip()