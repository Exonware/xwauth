#!/usr/bin/env python3
"""
#exonware/xwauth/tests/verify_installation.py
Installation Verification
Quick test to verify xwauth is properly installed and importable.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 20-Dec-2025
"""


def test_import():
    """Test that xwauth can be imported."""
    try:
        import exonware.xwauth
        assert hasattr(exonware.xwauth, 'XWAuth')
        assert hasattr(exonware.xwauth, 'XWAuthError')
        print("✅ xwauth imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import xwauth: {e}")
        return False
if __name__ == "__main__":
    test_import()
