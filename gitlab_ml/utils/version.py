import re
from typing import Optional, Tuple

import semver
from typer import BadParameter


def validate_version(version: str) -> str:
    """Validate and normalize a semantic version string."""
    try:
        # Parse and validate version
        ver = semver.VersionInfo.parse(version)
        return str(ver)
    except ValueError as e:
        raise BadParameter(
            f"Invalid version format: {version}. Must be a valid semantic version (e.g., 1.0.0)"
        ) from e


def increment_version(
    current_version: str,
    increment: str = "patch",
) -> str:
    """Increment a semantic version string."""
    ver = semver.VersionInfo.parse(current_version)
    
    if increment == "major":
        ver = ver.bump_major()
    elif increment == "minor":
        ver = ver.bump_minor()
    else:  # patch
        ver = ver.bump_patch()
    
    return str(ver)


def parse_version_range(version_spec: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse a version range specification (e.g., '>1.0.0 <=2.0.0')."""
    pattern = r"([<>]=?|=)\s*(\d+\.\d+\.\d+)"
    matches = re.findall(pattern, version_spec)
    
    min_version = None
    max_version = None
    
    for op, ver in matches:
        if op in (">=", ">"):
            min_version = ver
        elif op in ("<=", "<"):
            max_version = ver
        elif op == "=":
            min_version = max_version = ver
    
    return min_version, max_version 