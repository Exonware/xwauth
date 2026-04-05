#!/usr/bin/env python3
"""
#exonware/xwauth/tests/3.advance/runner.py
Runner for advance tests (3.advance layer).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1
Generation Date: 07-Jan-2025
"""

import sys
from pathlib import Path
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()
# Add src to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
# Import reusable utilities
from exonware.xwsystem.utils.test_runner import TestRunner


def main():
    """Run advance tests."""
    test_dir = Path(__file__).parent
    # Parse arguments for specific advance test categories
    args = sys.argv[1:]
    markers = ["xwauth_advance"]
    if "--security" in args:
        markers.append("xwauth_security")
    elif "--performance" in args:
        markers.append("xwauth_performance")
    elif "--usability" in args:
        markers.append("xwauth_usability")
    elif "--maintainability" in args:
        markers.append("xwauth_maintainability")
    elif "--extensibility" in args:
        markers.append("xwauth_extensibility")
    runner = TestRunner(
        library_name="xwauth",
        layer_name="3.advance",
        description="Advance Tests - Production Excellence Validation",
        test_dir=test_dir,
        markers=markers
    )
    return runner.run()
if __name__ == "__main__":
    sys.exit(main())
