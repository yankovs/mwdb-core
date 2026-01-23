"""
IOC (Indicator of Compromise) type definitions and validation utilities
"""

import re
from enum import Enum
from typing import Dict, Pattern


class IOCType(Enum):
    """Supported IOC types"""
    IP = "ip"
    IPRANGE = "iprange"
    URL = "url"
    DOMAIN = "domain"
    EMAIL = "email"
    HASH_MD5 = "md5"
    HASH_SHA1 = "sha1"
    HASH_SHA256 = "sha256"
    HASH_SHA512 = "sha512"
    HASH_SSDEEP = "ssdeep"
    FILE_PATH = "file_path"
    REGISTRY_KEY = "registry_key"
    C2_URL = "c2_url"
    MUTEX = "mutex"
    PROCESS_NAME = "process_name"


class IOCSeverity(Enum):
    """IOC severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IOCTypeGroup(Enum):
    """Logical grouping of IOC types for UI and search"""
    NETWORK = "network"
    HASH = "hash"
    FILE_SYSTEM = "file_system"
    PROCESS = "process"
    CONFIGURATION = "configuration"


# Mapping of IOC types to their logical groups
IOC_TYPE_GROUPS: Dict[IOCType, IOCTypeGroup] = {
    IOCType.IP: IOCTypeGroup.NETWORK,
    IOCType.IPRANGE: IOCTypeGroup.NETWORK,
    IOCType.URL: IOCTypeGroup.NETWORK,
    IOCType.DOMAIN: IOCTypeGroup.NETWORK,
    IOCType.EMAIL: IOCTypeGroup.NETWORK,
    IOCType.C2_URL: IOCTypeGroup.NETWORK,
    
    IOCType.HASH_MD5: IOCTypeGroup.HASH,
    IOCType.HASH_SHA1: IOCTypeGroup.HASH,
    IOCType.HASH_SHA256: IOCTypeGroup.HASH,
    IOCType.HASH_SHA512: IOCTypeGroup.HASH,
    IOCType.HASH_SSDEEP: IOCTypeGroup.HASH,
    
    IOCType.FILE_PATH: IOCTypeGroup.FILE_SYSTEM,
    IOCType.REGISTRY_KEY: IOCTypeGroup.FILE_SYSTEM,
    
    IOCType.PROCESS_NAME: IOCTypeGroup.PROCESS,
    IOCType.MUTEX: IOCTypeGroup.PROCESS,
    
    IOCType.C2_URL: IOCTypeGroup.CONFIGURATION,
}


# Validation regexes for each IOC type
IOC_VALIDATORS: Dict[IOCType, Pattern] = {
    # IPv4 and IPv6 addresses
    IOCType.IP: re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        r'|'
        r'^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$',
        re.IGNORECASE
    ),
    
    # CIDR notation for IP ranges
    IOCType.IPRANGE: re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        r'/(?:[0-9]|[1-2][0-9]|3[0-2])$|'
        r'^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}/[0-9]{1,3}$',
        re.IGNORECASE
    ),
    
    # URLs
    IOCType.URL: re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$',
        re.IGNORECASE
    ),
    
    # Domain names (including subdomains)
    IOCType.DOMAIN: re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    ),
    
    # Email addresses
    IOCType.EMAIL: re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    ),
    
    # MD5 hash (32 hex characters)
    IOCType.HASH_MD5: re.compile(r'^[a-fA-F0-9]{32}$'),
    
    # SHA1 hash (40 hex characters)
    IOCType.HASH_SHA1: re.compile(r'^[a-fA-F0-9]{40}$'),
    
    # SHA256 hash (64 hex characters)
    IOCType.HASH_SHA256: re.compile(r'^[a-fA-F0-9]{64}$'),
    
    # SHA512 hash (128 hex characters)
    IOCType.HASH_SHA512: re.compile(r'^[a-fA-F0-9]{128}$'),
    
    # SSDEEP/fuzzy hash
    IOCType.HASH_SSDEEP: re.compile(r'^\d+:\w+:\w+$'),
    
    # File paths (Windows and Unix)
    IOCType.FILE_PATH: re.compile(
        r'^(?:[a-zA-Z]:\\(?:\\[^\\/:*?"<>|\r\n]+)*\\?'
        r'|/'
        r'(?:[^/\x00]+/)*[^/\x00]*)',
        re.IGNORECASE
    ),
    
    # Windows registry keys
    IOCType.REGISTRY_KEY: re.compile(
        r'^HKEY_(?:CLASSES_ROOT|CURRENT_USER|LOCAL_MACHINE|USERS|PERFORMANCE_DATA|'
        r'CURRENT_CONFIG|DYN_DATA)\\.*',
        re.IGNORECASE
    ),
    
    # C2 URLs
    IOCType.C2_URL: re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$',
        re.IGNORECASE
    ),
    
    # Mutex names
    IOCType.MUTEX: re.compile(r'^[a-zA-Z0-9_\-\.]{1,256}$'),
    
    # Process names
    IOCType.PROCESS_NAME: re.compile(r'^[a-zA-Z0-9_\-\.\\]{1,256}\.exe$', re.IGNORECASE),
}


# Human-readable descriptions for each IOC type
IOC_TYPE_DESCRIPTIONS: Dict[IOCType, str] = {
    IOCType.IP: "IPv4 or IPv6 address",
    IOCType.IPRANGE: "CIDR IP address range",
    IOCType.URL: "Uniform Resource Locator",
    IOCType.DOMAIN: "Domain name",
    IOCType.EMAIL: "Email address",
    IOCType.HASH_MD5: "MD5 hash",
    IOCType.HASH_SHA1: "SHA1 hash",
    IOCType.HASH_SHA256: "SHA256 hash",
    IOCType.HASH_SHA512: "SHA512 hash",
    IOCType.HASH_SSDEEP: "SSDEEP/fuzzy hash",
    IOCType.FILE_PATH: "File path",
    IOCType.REGISTRY_KEY: "Windows registry key",
    IOCType.C2_URL: "Command and Control URL",
    IOCType.MUTEX: "Mutex name",
    IOCType.PROCESS_NAME: "Process name",
}


def validate_severity(severity):
    """
    Validate severity value.
    Accepts IOCSeverity enum or string value.
    
    Args:
        severity: IOCSeverity enum or string value
        
    Returns:
        IOCSeverity enum
        
    Raises:
        ValueError: If severity is invalid
    """
    if isinstance(severity, IOCSeverity):
        return severity
    
    if isinstance(severity, str):
        try:
            return IOCSeverity(severity)
        except ValueError:
            valid = [s.value for s in IOCSeverity]
            raise ValueError(
                f"Invalid severity: {severity}. Must be one of {valid}"
            )
    
    raise ValueError(f"Severity must be IOCSeverity enum or string, got {type(severity)}")


def validate_ioc(ioc_type: IOCType, value: str) -> bool:
    """
    Validate an IOC value against its type's regex pattern.
    
    Args:
        ioc_type: The IOC type to validate against (IOCType enum)
        value: The value to validate
        
    Returns:
        True if the value matches the type's pattern, False otherwise
        
    Raises:
        ValueError: If ioc_type is not a valid IOCType enum
    """
    if not isinstance(ioc_type, IOCType):
        raise ValueError(f"ioc_type must be IOCType enum, got {type(ioc_type)}")
    
    if ioc_type not in IOC_VALIDATORS:
        raise ValueError(f"Unknown IOC type: {ioc_type}")
    
    pattern = IOC_VALIDATORS[ioc_type]
    return pattern.match(value.strip()) is not None


def get_ioc_type_from_value(value: str) -> IOCType:
    """
    Attempt to auto-detect IOC type from value.
    Returns the first matching type, with priority given to hash types.
    
    Args:
        value: The value to analyze
        
    Returns:
        The detected IOC type, or None if no match found
    """
    value = value.strip().lower()
    
    # Check hash types first (more specific)
    hash_types = [
        IOCType.HASH_MD5,
        IOCType.HASH_SHA1,
        IOCType.HASH_SHA256,
        IOCType.HASH_SHA512,
        IOCType.HASH_SSDEEP,
    ]
    
    for hash_type in hash_types:
        if validate_ioc(hash_type, value):
            return hash_type
    
    # Check other types
    for ioc_type in IOCType:
        if ioc_type not in hash_types and validate_ioc(ioc_type, value):
            return ioc_type
    
    return None
