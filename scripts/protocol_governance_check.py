#!/usr/bin/env python3
"""
Protocol governance checks for deviation register policy.
Fails when unresolved critical deviations are present.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re


ROW_RE = re.compile(r"^\|\s*DEV-[^|]+\|")


@dataclass(slots=True)
class DeviationRow:
    deviation_id: str
    severity: str
    status: str
    raw_line: str


def _parse_register(register_path: Path) -> list[DeviationRow]:
    rows: list[DeviationRow] = []
    for raw in register_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not ROW_RE.match(line):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 9:
            continue
        rows.append(
            DeviationRow(
                deviation_id=parts[0],
                severity=parts[3].lower(),
                status=parts[8].lower(),
                raw_line=line,
            )
        )
    return rows


def _evaluate(rows: list[DeviationRow]) -> tuple[list[DeviationRow], list[DeviationRow]]:
    open_critical = [row for row in rows if row.severity == "critical" and row.status != "closed"]
    open_high = [row for row in rows if row.severity == "high" and row.status != "closed"]
    return open_critical, open_high


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate protocol deviation governance register.")
    parser.add_argument(
        "--register",
        default="docs/REF_54_PROTOCOL_DEVIATION_REGISTER.md",
        help="Path to deviation register markdown file.",
    )
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Also fail when unresolved high-severity deviations exist.",
    )
    parser.add_argument(
        "--profile",
        choices=["A", "B", "C"],
        default="A",
        help="Protocol rigor profile. Profile C enforces fail-on-high by default.",
    )
    args = parser.parse_args()

    register_path = Path(args.register)
    if not register_path.exists():
        raise FileNotFoundError(f"Deviation register not found: {register_path}")
    rows = _parse_register(register_path)
    if not rows:
        print("No deviation rows found in register.")
        return 1

    open_critical, open_high = _evaluate(rows)
    print(f"deviations_total={len(rows)}")
    print(f"open_critical={len(open_critical)}")
    print(f"open_high={len(open_high)}")

    if open_critical:
        print("Unresolved critical deviations:")
        for row in open_critical:
            print(f" - {row.deviation_id}: {row.raw_line}")
        return 1

    fail_on_high = args.fail_on_high or args.profile == "C"
    if fail_on_high and open_high:
        print("Unresolved high deviations (fail-on-high enabled):")
        for row in open_high:
            print(f" - {row.deviation_id}: {row.raw_line}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
