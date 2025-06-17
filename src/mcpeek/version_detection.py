"""MCP specification version detection and compatibility mapping."""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .utils.logging import get_logger


@dataclass
class MCPVersionInfo:
    """Information about MCP specification version."""
    protocol_version: str
    specification_version: str
    detected_from: str
    compatibility_status: str
    supported_features: List[str]
    version_confidence: float


class MCPVersionDetector:
    """Detects MCP specification versions based on server capabilities and responses."""
    
    # Known MCP protocol versions and their specification mappings
    MCP_VERSION_MAP = {
        "2024-11-05": {
            "spec_version": "1.0.0",
            "features": [
                "basic_tools", "basic_resources", "basic_prompts",
                "json_rpc_2.0", "capability_negotiation", "initialization_handshake"
            ]
        },
        "2024-10-07": {
            "spec_version": "0.9.0",
            "features": [
                "basic_tools", "basic_resources", "json_rpc_2.0"
            ]
        },
        "2024-06-25": {
            "spec_version": "0.8.0",
            "features": [
                "basic_tools", "json_rpc_2.0"
            ]
        }
    }
    
    # Feature detection patterns
    FEATURE_PATTERNS = {
        "basic_tools": {
            "methods": ["tools/list", "tools/call"],
            "capabilities": ["tools"]
        },
        "basic_resources": {
            "methods": ["resources/list", "resources/read"],
            "capabilities": ["resources"]
        },
        "basic_prompts": {
            "methods": ["prompts/list", "prompts/get"],
            "capabilities": ["prompts"]
        },
        "advanced_resources": {
            "methods": ["resources/subscribe", "resources/unsubscribe"],
            "capabilities": ["resources.subscribe", "resources.listChanged"]
        },
        "sampling_support": {
            "capabilities": ["sampling"]
        },
        "experimental_features": {
            "capabilities": ["experimental"]
        },
        "roots_support": {
            "capabilities": ["roots", "roots.listChanged"]
        }
    }

    def __init__(self):
        """Initialize version detector."""
        self.logger = get_logger()

    def detect_version(
        self, 
        server_info: Dict[str, Any], 
        server_capabilities: Dict[str, Any],
        available_methods: Optional[List[str]] = None
    ) -> MCPVersionInfo:
        """
        Detect MCP specification version from server information and capabilities.
        
        Args:
            server_info: Server information from initialization
            server_capabilities: Server capabilities from initialization
            available_methods: List of methods server supports (optional)
            
        Returns:
            MCPVersionInfo with detected version information
        """
        self.logger.debug("Starting MCP version detection")
        
        # Extract protocol version from server info
        protocol_version = server_info.get("protocol_version", "unknown")
        
        # Detect features based on capabilities and methods
        detected_features = self._detect_features(server_capabilities, available_methods)
        
        # Map protocol version to specification version
        spec_version, confidence = self._map_protocol_to_spec(protocol_version, detected_features)
        
        # Determine detection source
        detection_source = self._determine_detection_source(protocol_version, server_capabilities)
        
        # Assess compatibility status
        compatibility_status = self._assess_compatibility(protocol_version, detected_features)
        
        version_info = MCPVersionInfo(
            protocol_version=protocol_version,
            specification_version=spec_version,
            detected_from=detection_source,
            compatibility_status=compatibility_status,
            supported_features=detected_features,
            version_confidence=confidence
        )
        
        self.logger.info(f"Detected MCP version: {spec_version} (protocol: {protocol_version}, confidence: {confidence:.2f})")
        return version_info

    def _detect_features(
        self, 
        capabilities: Dict[str, Any], 
        methods: Optional[List[str]] = None
    ) -> List[str]:
        """Detect supported features from capabilities and available methods."""
        detected_features = []
        methods = methods or []
        
        for feature_name, pattern in self.FEATURE_PATTERNS.items():
            # Check method patterns
            required_methods = pattern.get("methods", [])
            methods_satisfied = all(method in methods for method in required_methods) if methods else True
            
            # Check capability patterns
            required_capabilities = pattern.get("capabilities", [])
            capabilities_satisfied = self._check_capabilities(capabilities, required_capabilities)
            
            # Feature is supported if either methods or capabilities indicate support
            if methods_satisfied or capabilities_satisfied:
                detected_features.append(feature_name)
        
        # Always include JSON-RPC 2.0 as it's fundamental to MCP
        if "json_rpc_2.0" not in detected_features:
            detected_features.append("json_rpc_2.0")
            
        return detected_features

    def _check_capabilities(self, capabilities: Dict[str, Any], required: List[str]) -> bool:
        """Check if required capabilities are present in server capabilities."""
        for capability in required:
            if "." in capability:
                # Nested capability (e.g., "resources.subscribe")
                parts = capability.split(".")
                current = capabilities
                for part in parts:
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
            else:
                # Top-level capability
                if capability not in capabilities:
                    return False
        return True

    def _map_protocol_to_spec(self, protocol_version: str, features: List[str]) -> Tuple[str, float]:
        """Map protocol version and features to specification version with confidence."""
        if protocol_version in self.MCP_VERSION_MAP:
            # Direct protocol version mapping
            spec_info = self.MCP_VERSION_MAP[protocol_version]
            spec_version = spec_info["spec_version"]
            expected_features = spec_info["features"]
            
            # Calculate confidence based on feature overlap
            matching_features = set(features) & set(expected_features)
            confidence = len(matching_features) / len(expected_features) if expected_features else 0.0
            
            return spec_version, max(0.8, confidence)  # Minimum 80% confidence for known versions
        
        # Fallback: Infer version from features
        return self._infer_version_from_features(features)

    def _infer_version_from_features(self, features: List[str]) -> Tuple[str, float]:
        """Infer specification version from detected features when protocol version is unknown."""
        # Score each known version based on feature compatibility
        best_version = "unknown"
        best_score = 0.0
        
        for protocol_ver, spec_info in self.MCP_VERSION_MAP.items():
            expected_features = set(spec_info["features"])
            detected_features = set(features)
            
            # Calculate compatibility score
            if expected_features:
                overlap = len(expected_features & detected_features)
                missing = len(expected_features - detected_features)
                extra = len(detected_features - expected_features)
                
                # Score: overlap ratio minus penalty for missing features
                score = (overlap / len(expected_features)) - (missing * 0.1) + (extra * 0.05)
                
                if score > best_score:
                    best_score = score
                    best_version = spec_info["spec_version"]
        
        # Lower confidence for inferred versions
        confidence = min(0.7, best_score) if best_version != "unknown" else 0.0
        
        return best_version, confidence

    def _determine_detection_source(self, protocol_version: str, capabilities: Dict[str, Any]) -> str:
        """Determine primary source of version detection."""
        if protocol_version != "unknown":
            return f"protocol_version ({protocol_version})"
        elif capabilities:
            return "capability_analysis"
        else:
            return "feature_inference"

    def _assess_compatibility(self, protocol_version: str, features: List[str]) -> str:
        """Assess compatibility status of the detected version."""
        if protocol_version == "unknown":
            return "uncertain"
        
        if protocol_version in self.MCP_VERSION_MAP:
            expected_features = self.MCP_VERSION_MAP[protocol_version]["features"]
            missing_features = set(expected_features) - set(features)
            
            if not missing_features:
                return "fully_compatible"
            elif len(missing_features) <= 1:
                return "mostly_compatible"
            else:
                return "partially_compatible"
        
        return "unknown_version"

    def get_version_summary(self, version_info: MCPVersionInfo) -> Dict[str, Any]:
        """Get a summary of version information for display."""
        return {
            "protocol_version": version_info.protocol_version,
            "specification_version": version_info.specification_version,
            "compatibility": version_info.compatibility_status,
            "confidence": f"{version_info.version_confidence:.1%}",
            "detection_method": version_info.detected_from,
            "supported_features": len(version_info.supported_features),
            "features": version_info.supported_features
        }

    def is_compatible_with_client(self, version_info: MCPVersionInfo) -> bool:
        """Check if detected server version is compatible with this client."""
        # MCPeek client supports MCP protocol version 2024-11-05
        client_protocol = "2024-11-05"
        
        if version_info.protocol_version == client_protocol:
            return True
        
        # Check if server supports basic required features
        required_features = ["json_rpc_2.0", "basic_tools"]
        return all(feature in version_info.supported_features for feature in required_features)