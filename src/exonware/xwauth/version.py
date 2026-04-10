#!/usr/bin/env python3
"""
Centralized version management for eXonware xwauth.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
This module provides centralized version management for xwauth.
All version references should import from this module to ensure consistency.
"""

from datetime import datetime


def _today_release_date() -> str:
    """Return today's date in DD-MMM-YYYY."""
    return datetime.now().strftime("%d-%b-%Y")
__version__ = "0.0.1.7"
__author__ = "eXonware Backend Team"
__email__ = "connect@exonware.com"
__date__ = _today_release_date()
VERSION_MAJOR = 0
VERSION_MINOR = 0
VERSION_PATCH = 1
VERSION_BUILD = 7
VERSION_SUFFIX = ""
VERSION_STRING = __version__ + VERSION_SUFFIX


def get_version() -> str:
    """Get the current version string."""
    return VERSION_STRING


def get_date() -> str:
    """Get the release/update date (DD-MMM-YYYY)."""
    return __date__


def get_version_info() -> tuple:
    """Get version as a tuple (major, minor, patch, build)."""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH, VERSION_BUILD)


def get_version_dict() -> dict:
    """Get version information as a dictionary."""
    return {
        "version": VERSION_STRING,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "build": VERSION_BUILD,
        "suffix": VERSION_SUFFIX,
    }


def is_dev_version() -> bool:
    """Check if this is a development version."""
    return VERSION_SUFFIX in ("dev", "alpha", "beta") or VERSION_BUILD is not None


def is_release_version() -> bool:
    """Check if this is a release version."""
    return not is_dev_version()


__all__ = [
    "__version__",
    "__date__",
    "VERSION_MAJOR",
    "VERSION_MINOR",
    "VERSION_PATCH",
    "VERSION_BUILD",
    "VERSION_SUFFIX",
    "VERSION_STRING",
    "get_version",
    "get_date",
    "get_version_info",
    "get_version_dict",
    "is_dev_version",
    "is_release_version",
]
