#!/usr/bin/env python3
"""Regression suite for the bundled Thai XeLaTeX toolkit.

Runs one positive suite and two negative suites that MUST fail closed. TEXINPUTS
is set explicitly so tests can resolve the bundled thaiarxiv.sty from latex/.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
tests = root / "tests"
pre = root / "tools" / "preflight.py"


def run(name: str):
    env = os.environ.copy()
    existing = env.get("TEXINPUTS", "")
    env["TEXINPUTS"] = f"{root}:{existing}" if existing else f"{root}:"
    return subprocess.run(
        [sys.executable, str(pre), name],
        cwd=tests,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    pos = run("regression_features.tex")
    print(pos.stdout)
    if pos.returncode != 0:
        print("REGRESSION FAIL: positive feature suite failed")
        return 2

    neg = run("expected_fail_severe.tex")
    print(neg.stdout)
    if neg.returncode == 0 or "severe equation scaling" not in neg.stdout:
        print("REGRESSION FAIL: severe-equation negative test was not rejected as expected")
        return 2

    neg_table = run("expected_fail_table.tex")
    print(neg_table.stdout)
    if neg_table.returncode == 0 or "severe table scaling" not in neg_table.stdout:
        print("REGRESSION FAIL: severe-table negative test was not rejected as expected")
        return 2

    print("REGRESSION PASS: positive suite passed; severe equation and table suites failed closed as expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
