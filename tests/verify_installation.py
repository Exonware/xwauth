#!/usr/bin/env python3
"""
#exonware/xwauth-connect/tests/verify_installation.py
Installation Verification
Quick test to verify xwauth-connect is properly installed and importable.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""

import importlib


def test_import():
    """Test that xwauth-connect can be imported and exposes its canonical surface."""
    try:
        import exonware.xwauth.connect  # noqa: F401
        # Multi-provider surface: providers registry is mandatory.
        assert importlib.import_module("exonware.xwauth.connect.providers") is not None
        print("xwauth-connect imported successfully")
        return True
    except ImportError as e:
        print(f"Failed to import xwauth-connect: {e}")
        return False


if __name__ == "__main__":
    test_import()
