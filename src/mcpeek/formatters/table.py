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
        server_panel = self._create_server_info_panel(result.server_info, result.capabilities, result.version_info)
        console.print(server_panel)
        console.print()

        # Summary
        summary_text = f"[bold green]📊 Discovery Summary[/bold green]\n"
        summary_text += f"🛠️  Tools: [bold cyan]{len(result.tools)}[/bold cyan] | "
        summary_text += f"📄 Resources: [bold yellow]{len(result.resources)}[/bold yellow] | "
        summary_text += f"💬 Prompts: [bold magenta]{len(result.prompts)}[/bold magenta]"
        console.print(Panel(summary_text, title="📊 Summary", border_style="green"))
        console.print()

        # Tools Table
        if result.tools:
            tools_table = self._create_tools_table(result.tools, result.verbosity_level)
            console.print(Panel(tools_table, title="🛠️ Available Tools", border_style="blue"))
            console.print()

        # Resources Table
        if result.resources:
            resources_table = self._create_resources_table(result.resources, result.verbosity_level)
            console.print(Panel(resources_table, title="📄 Available Resources", border_style="yellow"))
            console.print()

        # Prompts Table
        if result.prompts:
            prompts_table = self._create_prompts_table(result.prompts, result.verbosity_level)
            console.print(Panel(prompts_table, title="💬 Available Prompts", border_style="magenta"))
            console.print()

        # Tool Exploration Results
        if result.tool_exploration:
            exploration_panel = self._create_tool_exploration_panel(result.tool_exploration)
            console.print(Panel(exploration_panel, title="🔍 Tool Exploration Results", border_style="cyan"))

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
                console.print(Panel(str(tool_result), title="🔧 Tool Result", border_style="green"))
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
                    title = f"📄 Resource Content {i+1}"
                    if "uri" in content:
                        title += f" ({content['uri']})"

                    content_panel = self._create_content_panel(content)
                    console.print(Panel(content_panel, title=title, border_style="cyan"))
                    if i < len(contents) - 1:
                        console.print()
            else:
                # Single content or empty
                content_panel = self._create_content_panel(contents[0] if contents else {})
                console.print(Panel(content_panel, title="📄 Resource Content", border_style="cyan"))
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

        console.print(Panel(error_text, title="❌ Error", border_style="red"))
        return output.getvalue()

    def _create_server_info_panel(self, server_info: Dict[str, Any], capabilities: Dict[str, Any], version_info: Dict[str, Any] = None) -> Panel:
        """Create server information panel."""
        info_text = ""

        # Version Information (show first if available)
        if version_info and version_info.get("status") != "not_detected":
            info_text += "[bold cyan]🔧 MCP Version Information[/bold cyan]\n"
            
            protocol_version = version_info.get("protocol_version", "unknown")
            spec_version = version_info.get("specification_version", "unknown")
            compatibility = version_info.get("compatibility", "unknown")
            confidence = version_info.get("confidence", "0%")
            
            # Color-code compatibility status with emojis
            if compatibility == "fully_compatible":
                compat_color = "green"
                compat_emoji = "✅"
            elif compatibility == "mostly_compatible":
                compat_color = "yellow"
                compat_emoji = "⚠️"
            elif compatibility == "partially_compatible":
                compat_color = "orange"
                compat_emoji = "🟡"
            else:
                compat_color = "red"
                compat_emoji = "❌"
                
            info_text += f"  📋 Protocol Version: [bold bright_blue]{protocol_version}[/bold bright_blue]\n"
            info_text += f"  📜 Specification Version: [bold bright_magenta]{spec_version}[/bold bright_magenta]\n"
            info_text += f"  {compat_emoji} Compatibility: [{compat_color}]{compatibility}[/{compat_color}]\n"
            info_text += f"  🎯 Detection Confidence: [bold bright_green]{confidence}[/bold bright_green]\n"
            info_text += f"  🔍 Detection Method: [dim]{version_info.get('detection_method', 'unknown')}[/dim]\n"
            
            # Show supported features count
            feature_count = version_info.get("supported_features", 0)
            info_text += f"  ⚡ Supported Features: [bold bright_cyan]{feature_count}[/bold bright_cyan]\n"
            info_text += "\n"

        # Server Information
        if server_info:
            info_text += "[bold bright_blue]🖥️  Server Information[/bold bright_blue]\n"
            for key, value in server_info.items():
                # Skip version_info as we already displayed it above
                if key != "version_info":
                    info_text += f"  📍 {key}: [bright_yellow]{value}[/bright_yellow]\n"
            info_text += "\n"

        # Capabilities Summary
        if capabilities:
            info_text += "[bold bright_green]⚡ Capabilities Summary[/bold bright_green]\n"
            capability_count = 0
            for key, value in capabilities.items():
                if isinstance(value, dict):
                    capability_count += len(value)
                elif value:
                    capability_count += 1
                    
            info_text += f"  📊 Total Capabilities: [bold bright_cyan]{len(capabilities)}[/bold bright_cyan]\n"
            for key, value in capabilities.items():
                if isinstance(value, dict) and value:
                    info_text += f"  🔧 {key}: [bold green]{len(value)} items[/bold green]\n"
                elif value:
                    info_text += f"  ✅ {key}: [bold green]enabled[/bold green]\n"

        return Panel(info_text.strip(), title="🖥️  Server Info", border_style="blue")

    def _create_tools_table(self, tools: List, verbosity: int) -> Table:
        """Create tools table based on verbosity level."""
        table = Table(box=box.ROUNDED)

        # Add columns based on verbosity
        table.add_column("🔧 Name", style="bold bright_blue")

        if verbosity >= 1:
            table.add_column("📝 Description", style="bright_white")

        if verbosity >= 2:
            table.add_column("⚙️  Parameters", style="bright_green")

        if verbosity >= 3:
            table.add_column("📋 Schema", style="bright_yellow")

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

        table.add_column("🔗 URI", style="bold bright_cyan")

        if verbosity >= 1:
            table.add_column("📄 Name", style="bright_blue")
            table.add_column("📝 Description", style="bright_white")

        if verbosity >= 2:
            table.add_column("🎭 MIME Type", style="bright_green")

        if verbosity >= 3:
            table.add_column("📊 Metadata", style="bright_yellow")

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

        table.add_column("💬 Name", style="bold bright_magenta")

        if verbosity >= 1:
            table.add_column("📝 Description", style="bright_white")

        if verbosity >= 2:
            table.add_column("⚙️  Parameters", style="bright_green")

        if verbosity >= 3:
            table.add_column("📋 Schema", style="bright_yellow")

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
    
    def _create_tool_exploration_panel(self, exploration_results: Dict[str, Any]) -> str:
        """Create tool exploration results panel."""
        if not exploration_results:
            return "[dim]No tool exploration performed[/dim]"
        
        if "error" in exploration_results:
            return f"[red]Tool exploration failed: {exploration_results['error']}[/red]"
        
        panel_text = ""
        successful_tools = []
        failed_tools = []
        
        # Categorize results
        for tool_name, result in exploration_results.items():
            if isinstance(result, dict):
                if result.get("status") == "success":
                    successful_tools.append((tool_name, result))
                else:
                    failed_tools.append((tool_name, result))
        
        # Summary
        total_explored = len(exploration_results)
        success_count = len(successful_tools)
        failed_count = len(failed_tools)
        
        panel_text += f"[bold green]Exploration Summary[/bold green]\n"
        panel_text += f"Total tools explored: {total_explored}\n"
        panel_text += f"Successful calls: [green]{success_count}[/green]\n"
        panel_text += f"Failed calls: [red]{failed_count}[/red]\n\n"
        
        # Show successful explorations
        if successful_tools:
            panel_text += "[bold green]✓ Successful Explorations[/bold green]\n"
            for tool_name, result in successful_tools:
                panel_text += f"  [green]•[/green] [bold]{tool_name}[/bold]\n"
                
                # Show a preview of the result if it's not too complex
                tool_result = result.get("result", {})
                if isinstance(tool_result, dict):
                    # Show first few keys or a summary
                    if "content" in tool_result:
                        content = tool_result["content"]
                        if isinstance(content, list) and len(content) > 0:
                            panel_text += f"    Result: {len(content)} items\n"
                        else:
                            preview = str(content)[:100]
                            if len(str(content)) > 100:
                                preview += "..."
                            panel_text += f"    Result: {preview}\n"
                    else:
                        # Show a few key-value pairs
                        preview_items = list(tool_result.items())[:2]
                        if preview_items:
                            for key, value in preview_items:
                                value_str = str(value)[:50]
                                if len(str(value)) > 50:
                                    value_str += "..."
                                panel_text += f"    {key}: {value_str}\n"
                elif isinstance(tool_result, list):
                    panel_text += f"    Result: List with {len(tool_result)} items\n"
                else:
                    preview = str(tool_result)[:100]
                    if len(str(tool_result)) > 100:
                        preview += "..."
                    panel_text += f"    Result: {preview}\n"
                
                panel_text += "\n"
        
        # Show failed explorations
        if failed_tools:
            panel_text += "[bold red]✗ Failed Explorations[/bold red]\n"
            for tool_name, result in failed_tools:
                panel_text += f"  [red]•[/red] [bold]{tool_name}[/bold]\n"
                error_msg = result.get("error", "Unknown error")
                status = result.get("status", "error")
                
                if status == "failed_empty_params":
                    panel_text += f"    [yellow]Requires parameters[/yellow]: {error_msg[:100]}\n"
                else:
                    panel_text += f"    [red]Error[/red]: {error_msg[:100]}\n"
                panel_text += "\n"
        
        return panel_text.strip()