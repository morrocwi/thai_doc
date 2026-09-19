#!/usr/bin/env python3
"""Mechanical fail-closed lint for Thai semantic rendering hazards.

This tool does NOT infer thought units or replace semantic review. It catches
patterns that are unsafe under the Thai World-Class Publication System,
especially for native Google Docs JUSTIFIED Thai body text.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

THAI = r"\u0E00-\u0E7F"
THAI_SPACE_THAI = re.compile(rf"([{THAI}]) ([{THAI}])")
THAI_BEFORE_SPACE = re.compile(rf"([{THAI}]) ")
SPACE_BEFORE_THAI = re.compile(rf" ([{THAI}])")
THAI_NBSP_THAI = re.compile(rf"([{THAI}])\u00A0([{THAI}])")
DOUBLE_ASCII_SPACE = re.compile(r"\S {2,}\S")
VISIBLE_ASCII_SPACE = re.compile(r"(?<=\S) (?=\S)")

# These are not universally wrong, but are high-risk when stranded at rendered
# line endings. The list is deliberately conservative and can be expanded.
ORPHAN_ENDINGS = (
    "หาก", "โดย", "ซึ่ง", "เพื่อ", "เมื่อ", "เพราะ", "แต่", "และ", "หรือ",
    "ดังนั้น", "อย่างไรก็ตาม", "โดยเฉพาะ", "รวมทั้ง", "ตลอดจน", "จาก", "กับ",
)

METADATA_PREFIXES = (
    "วันที่", "เรื่อง", "เรียน", "สิ่งที่ส่งมาด้วย", "อ้างถึง", "เลขที่", "โทร",
    "โทรศัพท์", "อีเมล", "เว็บไซต์", "ที่อยู่",
)


def is_metadata_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith(METADATA_PREFIXES):
        return True
    if "....." in s:
        return True
    if s.startswith(("#", "- [", "```", "|")):
        return True
    return False


def line_col(text: str, pos: int) -> tuple[int, int]:
    line = text.count("\n", 0, pos) + 1
    last_nl = text.rfind("\n", 0, pos)
    col = pos + 1 if last_nl < 0 else pos - last_nl
    return line, col


def excerpt(text: str, pos: int, radius: int = 24) -> str:
    lo = max(0, pos - radius)
    hi = min(len(text), pos + radius)
    return text[lo:hi].replace("\n", "↵")


def lint(text: str, mode: str, rendered_lines: bool) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []

    # Control characters commonly used as post-hoc layout patches.
    for ch, name in [("\u2060", "WORD JOINER U+2060"), ("\u200B", "ZERO WIDTH SPACE U+200B")]:
        start = 0
        while True:
            pos = text.find(ch, start)
            if pos < 0:
                break
            line, col = line_col(text, pos)
            failures.append(
                f"{name} found at {line}:{col}; recomposition must precede no-break/control-character repair; context={excerpt(text,pos)!r}"
            )
            start = pos + 1

    # NBSP between Thai characters is not an allowed generic breath separator.
    for m in THAI_NBSP_THAI.finditer(text):
        line, col = line_col(text, m.start() + 1)
        failures.append(
            f"Thai-to-Thai NBSP U+00A0 at {line}:{col}; NBSP is reserved for genuine protected atoms, not Thai breath rhythm; context={excerpt(text,m.start())!r}"
        )

    if mode == "google-docs-justified":
        # Hard gate: Google Docs justifies the whole line, not individual script
        # runs. Therefore a U+0020 inside an embedded English phrase can stretch
        # just as dramatically as Thai<->Latin or Thai<->Thai spacing. Once a
        # body line/paragraph is Thai-dominant, no visible-token ASCII word space
        # is allowed after renderer adaptation. Pure-English paragraphs are a
        # separate route and are not linted by this Thai-dominant gate.
        for i, line in enumerate(text.splitlines(), start=1):
            if is_metadata_line(line):
                continue
            if not re.search(rf"[{THAI}]", line):
                continue
            for m in VISIBLE_ASCII_SPACE.finditer(line):
                pos_in_line = m.start()
                # recover absolute position for useful context
                line_start = sum(len(x) + 1 for x in text.splitlines()[: i - 1])
                pos = line_start + pos_in_line
                failures.append(
                    f"Stretchable U+0020 SPACE inside Thai-dominant JUSTIFIED body at {i}:{pos_in_line+1}; no Latin-run exemption exists because Google Docs justifies the whole line. Classify lexical/breath/protected role and apply a non-stretching renderer separator; context={excerpt(text,max(0,pos-1))!r}"
                )
            if DOUBLE_ASCII_SPACE.search(line):
                failures.append(
                    f"Multiple ASCII spaces inside Thai JUSTIFIED body at line {i}; formatting gaps must not be used to encode breath strength"
                )

    if rendered_lines:
        for i, line in enumerate(text.splitlines(), start=1):
            s = line.rstrip()
            if not s or is_metadata_line(s):
                continue
            # Ignore punctuation-closed lines: the connector may be a citation or
            # quoted token if followed by punctuation, so only bare endings fail.
            for token in ORPHAN_ENDINGS:
                if s.endswith(token):
                    failures.append(
                        f"Potential orphan connector at rendered line {i}: {token!r}; repair by recomposing current + next 1-2 thought units before using any no-break character"
                    )
                    break

    # Diagnostic only: thin spaces are valid renderer adapters in the strict
    # Google Docs route, but a very high density can indicate spacing-first logic.
    thin_count = text.count("\u2009")
    thai_count = len(re.findall(rf"[{THAI}]", text))
    if thai_count >= 80 and thin_count > thai_count / 8:
        warnings.append(
            f"High U+2009 density ({thin_count} thin spaces / {thai_count} Thai codepoints); verify that separators follow semantic breath classification rather than a fixed cadence"
        )

    return failures, warnings


def self_test() -> int:
    good = "ภาษาไทยต้องเริ่มจากความหมาย\u2009แล้วจึงจัดจังหวะ\u2009ก่อนส่งให้ตัวจัดหน้า"
    bad_space = "ภาษาไทย ต้องเริ่มจากความหมาย"
    bad_mixed = "ภาคสนาม ARAYA พบว่า"
    bad_latin_run = "บริษัท\u2009(ARAYA NIKAH SOCIAL ENTERPRISE CO., LTD.)\u2009ดำเนินงาน"
    bad_joiner = "หาก\u2060กระทรวงเห็นสมควร"
    bad_render = "ข้อความอธิบายต่อเนื่อง หาก\nกระทรวงเห็นสมควรดำเนินการ"

    f, _ = lint(good, "google-docs-justified", False)
    if f:
        print("SELF-TEST FAIL: valid U+2009 sample rejected")
        print("\n".join(f))
        return 2

    f, _ = lint(bad_space, "google-docs-justified", False)
    if not any("U+0020" in x for x in f):
        print("SELF-TEST FAIL: Thai U+0020 hazard not detected")
        return 2

    f, _ = lint(bad_mixed, "google-docs-justified", False)
    if not any("U+0020" in x for x in f):
        print("SELF-TEST FAIL: mixed-script U+0020 hazard not detected")
        return 2

    f, _ = lint(bad_latin_run, "google-docs-justified", False)
    if not any("no Latin-run exemption" in x for x in f):
        print("SELF-TEST FAIL: embedded Latin-run U+0020 hazard not detected")
        return 2

    f, _ = lint(bad_joiner, "google-docs-justified", False)
    if not any("WORD JOINER" in x for x in f):
        print("SELF-TEST FAIL: WORD JOINER hazard not detected")
        return 2

    f, _ = lint(bad_render, "generic", True)
    if not any("orphan connector" in x.lower() for x in f):
        print("SELF-TEST FAIL: rendered orphan hazard not detected")
        return 2

    print("PASS thai_semantic_lint self-test")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="UTF-8 text/markdown file to inspect")
    ap.add_argument(
        "--mode",
        choices=["generic", "google-docs-justified"],
        default="generic",
        help="apply route-specific mechanical gates",
    )
    ap.add_argument(
        "--rendered-lines",
        action="store_true",
        help="treat physical newlines as rendered line endings and flag orphan connectors",
    )
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.file:
        ap.error("file is required unless --self-test is used")

    path = Path(args.file)
    text = path.read_text(encoding="utf-8", errors="replace")
    failures, warnings = lint(text, args.mode, args.rendered_lines)

    if warnings:
        print("THAI SEMANTIC LINT WARN:")
        for w in warnings:
            print(" -", w)
    if failures:
        print("THAI SEMANTIC LINT FAIL:")
        for f in failures:
            print(" -", f)
        return 2

    print("THAI SEMANTIC LINT PASS: no mechanical separator/control-character blockers detected")
    print("NOTE: PASS does not prove semantic rhythm; thought-unit, breath, lookahead, and rendered visual review remain mandatory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
