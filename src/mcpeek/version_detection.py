"""MCP specification version detection and compatibility mapping."""

import json
import os
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
    
    # Score calculation weights and thresholds
    MISSING_FEATURE_PENALTY = 0.1
    EXTRA_FEATURE_BONUS = 0.05
    MIN_KNOWN_VERSION_CONFIDENCE = 0.8
    MAX_INFERRED_CONFIDENCE = 0.7
    
    # Default MCP protocol versions and their specification mappings
    DEFAULT_VERSION_MAP = {
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

    def __init__(self, version_map: Optional[Dict[str, Any]] = None, version_map_file: Optional[str] = None):
        """
        Initialize version detector.
        
        Args:
            version_map: Custom version mapping dictionary (optional)
            version_map_file: Path to JSON file containing version mapping (optional)
        """
        self.logger = get_logger()
        self.version_map = self._load_version_map(version_map, version_map_file)
    
    def _load_version_map(self, version_map: Optional[Dict[str, Any]], version_map_file: Optional[str]) -> Dict[str, Any]:
        """Load version mapping from parameter, file, or use default."""
        if version_map:
            self.logger.debug("Using provided version mapping")
            return version_map
        
        if version_map_file and os.path.exists(version_map_file):
            try:
                with open(version_map_file, 'r', encoding='utf-8') as f:
                    loaded_map = json.load(f)
                self.logger.debug(f"Loaded version mapping from {version_map_file}")
                return loaded_map
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to load version mapping from {version_map_file}: {e}")
        
        # Check for environment variable pointing to config file
        env_config_file = os.environ.get('MCPEEK_VERSION_MAP_FILE')
        if env_config_file and os.path.exists(env_config_file):
            try:
                with open(env_config_file, 'r', encoding='utf-8') as f:
                    loaded_map = json.load(f)
                self.logger.debug(f"Loaded version mapping from environment file {env_config_file}")
                return loaded_map
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to load version mapping from environment file {env_config_file}: {e}")
        
        self.logger.debug("Using default version mapping")
        return self.DEFAULT_VERSION_MAP

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
        
        protocol_version = server_info.get("protocol_version", "unknown")
        detected_features = self._detect_features(server_capabilities, available_methods)
        
        version_info = self._create_version_info(
            protocol_version, detected_features, server_capabilities
        )
        
        self.logger.info(f"Detected MCP version: {version_info.specification_version} "
                        f"(protocol: {protocol_version}, confidence: {version_info.version_confidence:.2f})")
        return version_info
    
    def _create_version_info(
        self, 
        protocol_version: str, 
        detected_features: List[str], 
        server_capabilities: Dict[str, Any]
    ) -> MCPVersionInfo:
        """Create MCPVersionInfo from detected components."""
        # Map protocol version to specification version
        spec_version, confidence = self._map_protocol_to_spec(protocol_version, detected_features)
        
        # Determine detection source
        detection_source = self._determine_detection_source(protocol_version, server_capabilities)
        
        # Assess compatibility status
        compatibility_status = self._assess_compatibility(protocol_version, detected_features)
        
        return MCPVersionInfo(
            protocol_version=protocol_version,
            specification_version=spec_version,
            detected_from=detection_source,
            compatibility_status=compatibility_status,
            supported_features=detected_features,
            version_confidence=confidence
        )

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
            methods_satisfied = False
            if required_methods and methods:
                methods_satisfied = all(method in methods for method in required_methods)
            elif not required_methods:
                # No methods required for this feature
                methods_satisfied = True
            
            # Check capability patterns
            required_capabilities = pattern.get("capabilities", [])
            capabilities_satisfied = self._check_capabilities(capabilities, required_capabilities)
            
            # Feature is supported if:
            # 1. Both methods and capabilities are satisfied (when both are required), OR
            # 2. Only methods are required and satisfied, OR 
            # 3. Only capabilities are required and satisfied
            has_method_requirement = bool(required_methods)
            has_capability_requirement = bool(required_capabilities)
            
            if has_method_requirement and has_capability_requirement:
                # Both required - need both satisfied
                feature_supported = methods_satisfied and capabilities_satisfied
            elif has_method_requirement:
                # Only methods required
                feature_supported = methods_satisfied
            elif has_capability_requirement:
                # Only capabilities required
                feature_supported = capabilities_satisfied
            else:
                # No requirements - feature supported
                feature_supported = True
                
            if feature_supported:
                detected_features.append(feature_name)
        
        # Always include JSON-RPC 2.0 as it's fundamental to MCP
        if "json_rpc_2.0" not in detected_features:
            detected_features.append("json_rpc_2.0")
            
        return detected_features

    def _check_capabilities(self, capabilities: Dict[str, Any], required: List[str]) -> bool:
        """Check if required capabilities are present in server capabilities."""
        if not isinstance(capabilities, dict) or not isinstance(required, list):
            return False
            
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
        if protocol_version in self.version_map:
            # Direct protocol version mapping
            spec_info = self.version_map[protocol_version]
            spec_version = spec_info["spec_version"]
            expected_features = spec_info["features"]
            
            # Calculate confidence based on feature overlap
            matching_features = set(features) & set(expected_features)
            confidence = len(matching_features) / len(expected_features) if expected_features else 0.0
            
            # Return actual confidence without artificial minimum
            # High confidence indicates this is a known protocol version
            return spec_version, max(confidence, 0.9) if confidence >= 0.7 else confidence
        
        # Fallback: Infer version from features
        return self._infer_version_from_features(features)

    def _infer_version_from_features(self, features: List[str]) -> Tuple[str, float]:
        """Infer specification version from detected features when protocol version is unknown."""
        # Score each known version based on feature compatibility
        best_version = "unknown"
        best_score = 0.0
        
        for protocol_ver, spec_info in self.version_map.items():
            expected_features = set(spec_info["features"])
            detected_features = set(features)
            
            # Calculate compatibility score
            if expected_features:
                overlap = len(expected_features & detected_features)
                missing = len(expected_features - detected_features)
                extra = len(detected_features - expected_features)
                
                # Score: overlap ratio minus penalty for missing features
                score = (overlap / len(expected_features)) - (missing * self.MISSING_FEATURE_PENALTY) + (extra * self.EXTRA_FEATURE_BONUS)
                
                if score > best_score:
                    best_score = score
                    best_version = spec_info["spec_version"]
        
        # Lower confidence for inferred versions
        confidence = min(self.MAX_INFERRED_CONFIDENCE, best_score) if best_version != "unknown" else 0.0
        
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
        
        if protocol_version in self.version_map:
            expected_features = self.version_map[protocol_version]["features"]
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