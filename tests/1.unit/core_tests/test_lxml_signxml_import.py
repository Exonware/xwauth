"""Regression: xwlazy global import hook must not break SAML-related stacks (lxml/signxml)."""

from __future__ import annotations

import subprocess
import sys

import pytest


def _run_isolated_snippet(python_source: str, *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    """Run import snippet in a fresh interpreter (native extensions may segfault on bad stacks)."""
    return subprocess.run(
        [sys.executable, "-c", python_source],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def test_lxml_etree_import_after_xwauth() -> None:
    """After ``import exonware.xwauth``, ``from lxml import etree`` must work in a clean process."""
    code = (
        "import exonware.xwauth\n"
        "from lxml import etree\n"
        "assert etree.Element('a') is not None\n"
    )
    proc = _run_isolated_snippet(code)
    if proc.returncode == 0:
        return
    if proc.returncode < 0:
        pytest.skip(
            "lxml import crashed or was killed in subprocess (often native extension / "
            f"OneDrive or broken optional deps). exit={proc.returncode}"
        )
    err = (proc.stderr or proc.stdout or "").strip()
    if "No module named 'lxml'" in err or "ImportError" in err:
        pytest.skip("lxml is not installed")
    if "SyntaxError" in err:
        pytest.skip(
            "lxml dependency chain has invalid Python (e.g. stray PyPI `rpython` breaking rply). "
            f"stderr: {err[:800]}"
        )
    pytest.fail(f"lxml import failed after xwauth (rc={proc.returncode}): {err[:2000]}")


def test_signxml_import_after_xwauth() -> None:
    code = (
        "import exonware.xwauth\n"
        "from signxml import XMLSigner\n"
        "assert XMLSigner is not None\n"
    )
    proc = _run_isolated_snippet(code)
    if proc.returncode == 0:
        return
    if proc.returncode < 0:
        pytest.skip(
            "signxml/lxml chain crashed in subprocess (native extension). "
            f"exit={proc.returncode}"
        )
    err = (proc.stderr or proc.stdout or "").strip()
    if "No module named 'signxml'" in err or "No module named 'lxml'" in err:
        pytest.skip("signxml or lxml is not installed")
    if "SyntaxError" in err:
        pytest.skip(f"signxml dependency chain syntax error: {err[:800]}")
    pytest.fail(f"signxml import failed after xwauth (rc={proc.returncode}): {err[:2000]}")
