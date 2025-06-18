"""Markdown output formatting."""

from typing import Dict, Any, List
from .base import BaseFormatter, DiscoveryResult
from ..utils.helpers import safe_json_dumps, extract_error_details


class MarkdownFormatter(BaseFormatter):
    """Markdown output formatting."""

    def __init__(self):
        """Initialize markdown formatter."""
        super().__init__()

    def format_discovery_result(self, result: DiscoveryResult) -> str:
        """Format discovery results as markdown."""
        output = []
        
        # Title
        output.append("# MCP Endpoint Discovery Results")
        output.append("")
        
        # Summary
        output.append("## 📊 Summary")
        output.append("")
        output.append(f"- **Tools**: {len(result.tools)}")
        output.append(f"- **Resources**: {len(result.resources)}")
        output.append(f"- **Prompts**: {len(result.prompts)}")
        output.append(f"- **Verbosity Level**: {result.verbosity_level}")
        output.append("")
        
        # Server Information
        if result.server_info:
            output.append("## 🖥️ Server Information")
            output.append("")
            for key, value in result.server_info.items():
                if key != "version_info":
                    output.append(f"- **{key}**: {value}")
            output.append("")
        
        # Version Information
        if result.version_info and result.version_info.get("status") != "not_detected":
            output.append("## 🔧 MCP Version Information")
            output.append("")
            version_info = result.version_info
            
            protocol_version = version_info.get("protocol_version", "unknown")
            spec_version = version_info.get("specification_version", "unknown")
            compatibility = version_info.get("compatibility", "unknown")
            confidence = version_info.get("confidence", "0%")
            
            # Add status emoji based on compatibility
            if compatibility == "fully_compatible":
                status_emoji = "✅"
            elif compatibility == "mostly_compatible":
                status_emoji = "⚠️"
            elif compatibility == "partially_compatible":
                status_emoji = "🟡"
            else:
                status_emoji = "❌"
            
            output.append(f"- **Protocol Version**: {protocol_version}")
            output.append(f"- **Specification Version**: {spec_version}")
            output.append(f"- **Compatibility**: {status_emoji} {compatibility}")
            output.append(f"- **Detection Confidence**: {confidence}")
            output.append(f"- **Detection Method**: {version_info.get('detection_method', 'unknown')}")
            
            feature_count = version_info.get("supported_features", 0)
            output.append(f"- **Supported Features**: {feature_count}")
            output.append("")
        
        # Capabilities
        if result.capabilities:
            output.append("## ⚡ Capabilities")
            output.append("")
            for key, value in result.capabilities.items():
                if isinstance(value, dict) and value:
                    output.append(f"- **{key}**: {len(value)} items")
                elif value:
                    output.append(f"- **{key}**: enabled")
            output.append("")
        
        # Tools
        if result.tools:
            output.append("## 🛠️ Available Tools")
            output.append("")
            for tool in result.tools:
                output.append(f"### 🔧 {tool.name}")
                output.append("")
                
                if tool.description:
                    output.append(f"**Description**: {tool.description}")
                    output.append("")
                
                if result.verbosity_level >= 2 and tool.parameters:
                    output.append("**Parameters**:")
                    output.append("")
                    params_formatted = self.format_parameter_info(tool.parameters, result.verbosity_level)
                    if params_formatted != "None":
                        output.append(f"```")
                        output.append(params_formatted)
                        output.append(f"```")
                    else:
                        output.append("- None")
                    output.append("")
                
                if result.verbosity_level >= 3 and tool.schema:
                    output.append("**Schema**:")
                    output.append("")
                    output.append("```json")
                    output.append(safe_json_dumps(tool.schema, pretty=True))
                    output.append("```")
                    output.append("")
        
        # Resources
        if result.resources:
            output.append("## 📄 Available Resources")
            output.append("")
            for resource in result.resources:
                output.append(f"### 📎 {resource.name or resource.uri}")
                output.append("")
                
                output.append(f"**URI**: `{resource.uri}`")
                output.append("")
                
                if resource.description:
                    output.append(f"**Description**: {resource.description}")
                    output.append("")
                
                if result.verbosity_level >= 2:
                    if resource.mime_type:
                        output.append(f"**MIME Type**: `{resource.mime_type}`")
                        output.append("")
                
                if result.verbosity_level >= 3 and resource.metadata:
                    output.append("**Metadata**:")
                    output.append("")
                    output.append("```json")
                    output.append(safe_json_dumps(resource.metadata, pretty=True))
                    output.append("```")
                    output.append("")
        
        # Prompts
        if result.prompts:
            output.append("## 💬 Available Prompts")
            output.append("")
            for prompt in result.prompts:
                output.append(f"### 💭 {prompt.name}")
                output.append("")
                
                if prompt.description:
                    output.append(f"**Description**: {prompt.description}")
                    output.append("")
                
                if result.verbosity_level >= 2 and prompt.parameters:
                    output.append("**Parameters**:")
                    output.append("")
                    params_formatted = self.format_parameter_info(prompt.parameters, result.verbosity_level)
                    if params_formatted != "None":
                        output.append(f"```")
                        output.append(params_formatted)
                        output.append(f"```")
                    else:
                        output.append("- None")
                    output.append("")
                
                if result.verbosity_level >= 3 and prompt.schema:
                    output.append("**Schema**:")
                    output.append("")
                    output.append("```json")
                    output.append(safe_json_dumps(prompt.schema, pretty=True))
                    output.append("```")
                    output.append("")
        
        # Tool Exploration Results
        if result.tool_exploration:
            output.append("## 🔍 Tool Exploration Results")
            output.append("")
            
            if "error" in result.tool_exploration:
                output.append(f"❌ **Error**: {result.tool_exploration['error']}")
                output.append("")
            else:
                successful_tools = []
                failed_tools = []
                
                # Categorize results
                for tool_name, tool_result in result.tool_exploration.items():
                    if isinstance(tool_result, dict):
                        if tool_result.get("status") == "success":
                            successful_tools.append((tool_name, tool_result))
                        else:
                            failed_tools.append((tool_name, tool_result))
                
                # Summary
                total_explored = len(result.tool_exploration)
                success_count = len(successful_tools)
                failed_count = len(failed_tools)
                
                output.append(f"- **Total tools explored**: {total_explored}")
                output.append(f"- **Successful calls**: ✅ {success_count}")
                output.append(f"- **Failed calls**: ❌ {failed_count}")
                output.append("")
                
                # Show successful explorations
                if successful_tools:
                    output.append("### ✅ Successful Explorations")
                    output.append("")
                    for tool_name, tool_result in successful_tools:
                        output.append(f"#### 🔧 {tool_name}")
                        output.append("")
                        
                        # Show a preview of the result
                        result_data = tool_result.get("result", {})
                        if isinstance(result_data, dict):
                            if "content" in result_data:
                                content = result_data["content"]
                                if isinstance(content, list):
                                    output.append(f"**Result**: List with {len(content)} items")
                                else:
                                    preview = str(content)[:200]
                                    if len(str(content)) > 200:
                                        preview += "..."
                                    output.append(f"**Result**: {preview}")
                            else:
                                # Show a few key-value pairs
                                preview_items = list(result_data.items())[:3]
                                if preview_items:
                                    output.append("**Result**:")
                                    for key, value in preview_items:
                                        value_str = str(value)[:100]
                                        if len(str(value)) > 100:
                                            value_str += "..."
                                        output.append(f"- **{key}**: {value_str}")
                        elif isinstance(result_data, list):
                            output.append(f"**Result**: List with {len(result_data)} items")
                        else:
                            preview = str(result_data)[:200]
                            if len(str(result_data)) > 200:
                                preview += "..."
                            output.append(f"**Result**: {preview}")
                        
                        output.append("")
                
                # Show failed explorations
                if failed_tools:
                    output.append("### ❌ Failed Explorations")
                    output.append("")
                    for tool_name, tool_result in failed_tools:
                        output.append(f"#### 🔧 {tool_name}")
                        output.append("")
                        
                        error_msg = tool_result.get("error", "Unknown error")
                        status = tool_result.get("status", "error")
                        
                        if status == "failed_empty_params":
                            output.append(f"⚠️ **Requires parameters**: {error_msg[:200]}")
                        else:
                            output.append(f"❌ **Error**: {error_msg[:200]}")
                        output.append("")
        
        return "\n".join(output)

    def format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool execution results as markdown."""
        output = []
        
        output.append("# 🔧 Tool Execution Result")
        output.append("")
        
        if "result" in result:
            tool_result = result["result"]
            output.append("## ✅ Result")
            output.append("")
            
            if isinstance(tool_result, dict):
                output.append("```json")
                output.append(safe_json_dumps(tool_result, pretty=True))
                output.append("```")
            elif isinstance(tool_result, list):
                output.append("```json")
                output.append(safe_json_dumps(tool_result, pretty=True))
                output.append("```")
            else:
                output.append(f"```")
                output.append(str(tool_result))
                output.append("```")
        else:
            # Show full result
            output.append("## 📋 Full Result")
            output.append("")
            output.append("```json")
            output.append(safe_json_dumps(result, pretty=True))
            output.append("```")
        
        output.append("")
        return "\n".join(output)

    def format_resource_result(self, result: Dict[str, Any]) -> str:
        """Format resource read results as markdown."""
        output = []
        
        output.append("# 📄 Resource Content")
        output.append("")
        
        if "contents" in result:
            contents = result["contents"]
            if isinstance(contents, list) and contents:
                # Multiple content items
                for i, content in enumerate(contents):
                    title = f"## 📎 Content {i+1}"
                    if "uri" in content:
                        title += f" - {content['uri']}"
                    output.append(title)
                    output.append("")
                    
                    output.extend(self._format_content_section(content))
                    
                    if i < len(contents) - 1:
                        output.append("---")
                        output.append("")
            else:
                # Single content or empty
                output.append("## 📎 Content")
                output.append("")
                content_item = contents[0] if contents else {}
                output.extend(self._format_content_section(content_item))
        else:
            # Show full result
            output.append("## 📋 Full Result")
            output.append("")
            output.append("```json")
            output.append(safe_json_dumps(result, pretty=True))
            output.append("```")
        
        output.append("")
        return "\n".join(output)
    
    def _format_content_section(self, content: Dict[str, Any]) -> List[str]:
        """Format a single content section."""
        section = []
        
        if "mimeType" in content:
            section.append(f"**MIME Type**: `{content['mimeType']}`")
            section.append("")
        
        if "uri" in content:
            section.append(f"**URI**: `{content['uri']}`")
            section.append("")
        
        if "text" in content:
            text_content = content["text"]
            section.append("**Content**:")
            section.append("")
            
            # Determine appropriate code block format based on MIME type
            mime_type = content.get("mimeType", "").lower()
            if "json" in mime_type:
                section.append("```json")
            elif "python" in mime_type or mime_type == "text/x-python":
                section.append("```python")
            elif "javascript" in mime_type or "js" in mime_type:
                section.append("```javascript")
            elif "html" in mime_type:
                section.append("```html")
            elif "xml" in mime_type:
                section.append("```xml")
            elif "markdown" in mime_type:
                section.append("```markdown")
            else:
                section.append("```")
            
            section.append(text_content)
            section.append("```")
            section.append("")
        elif "blob" in content:
            section.append(f"**Binary Content**: {len(content['blob'])} bytes")
            section.append("")
        
        return section

    def format_error(self, error: Exception) -> str:
        """Format error messages as markdown."""
        output = []
        
        output.append("# ❌ Error")
        output.append("")
        
        error_details = extract_error_details(error)
        
        output.append(f"**Error Type**: {error_details['type']}")
        output.append("")
        output.append(f"**Message**: {error_details['message']}")
        output.append("")
        
        if error_details.get('details'):
            output.append("**Details**:")
            output.append("")
            output.append("```json")
            output.append(safe_json_dumps(error_details['details'], pretty=True))
            output.append("```")
            output.append("")
        
        return "\n".join(output)

    def format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as markdown."""
        output = []
        
        output.append("## 📋 Data")
        output.append("")
        output.append("```json")
        output.append(safe_json_dumps(data, pretty=True))
        output.append("```")
        output.append("")
        
        return "\n".join(output)

    def format_list(self, data: List[Any]) -> str:
        """Format a list as markdown."""
        output = []
        
        output.append("## 📋 Data")
        output.append("")
        output.append("```json")
        output.append(safe_json_dumps(data, pretty=True))
        output.append("```")
        output.append("")
        
        return "\n".join(output)