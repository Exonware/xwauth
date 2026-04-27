# exonware/xwauth.connector/tests/1.unit/utils/test_lazy_mode_example.py
"""Validate lazy-install wiring: exonware.xwlazy.config_package_lazy_install_enabled (GUIDE_00_MASTER).

Runs in subprocesses so importing ``exonware.xwlazy`` never installs the global ``__import__``
hook in the pytest process (that breaks lxml/signxml used by SAML tests).
"""

from __future__ import annotations

import subprocess
import sys

import pytest


def _run_snippet(python_source: str, *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", python_source],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


@pytest.mark.xwauth_unit
def test_config_package_lazy_importable() -> None:
    code = (
        "from exonware.xwlazy import config_package_lazy_install_enabled\n"
        "assert callable(config_package_lazy_install_enabled)\n"
    )
    proc = _run_snippet(code)
    if proc.returncode == 0:
        return
    err = (proc.stderr or proc.stdout or "").strip()
    if "No module named 'exonware.xwlazy'" in err or "No module named \"exonware.xwlazy\"" in err:
        pytest.skip("exonware.xwlazy not installed")
    pytest.fail(f"xwlazy import failed (rc={proc.returncode}): {err[:2000]}")


@pytest.mark.xwauth_unit
def test_config_package_lazy_install_enabled_smoke() -> None:
    code = (
        "from exonware.xwlazy import config_package_lazy_install_enabled\n"
        "config_package_lazy_install_enabled('exonware.xwauth.connector', enabled=True, mode='smart')\n"
    )
    proc = _run_snippet(code)
    if proc.returncode == 0:
        return
    err = (proc.stderr or proc.stdout or "").strip()
    if "No module named 'exonware.xwlazy'" in err:
        pytest.skip("exonware.xwlazy not installed")
    pytest.fail(f"config_package_lazy_install_enabled smoke failed (rc={proc.returncode}): {err[:2000]}")


@pytest.mark.xwauth_unit
def test_config_package_lazy_install_enabled_disabled_noop() -> None:
    code = (
        "from exonware.xwlazy import config_package_lazy_install_enabled\n"
        "config_package_lazy_install_enabled('exonware.xwauth.connector', enabled=False, mode='smart')\n"
    )
    proc = _run_snippet(code)
    if proc.returncode == 0:
        return
    err = (proc.stderr or proc.stdout or "").strip()
    if "No module named 'exonware.xwlazy'" in err:
        pytest.skip("exonware.xwlazy not installed")
    pytest.fail(f"config_package_lazy_install_enabled disabled failed (rc={proc.returncode}): {err[:2000]}")
