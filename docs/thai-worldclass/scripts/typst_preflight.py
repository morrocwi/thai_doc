#!/usr/bin/env python3
"""Fail-closed preflight for the Typst v2.1 Thai route.

Static checks are always available. Compile verification requires Typst >= 0.15.1.
A missing/older CLI yields CANNOT VERIFY for --compile rather than a false PASS.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

MIN_VERSION = (0, 15, 1)
THAI_RE = re.compile(r"[\u0E00-\u0E7F]")
REPEATED_LAYOUT_SPACE = re.compile(r"\S {4,}\S")
THAI_TO_THAI_ASCII_SPACE = re.compile(r"[\u0E00-\u0E7F] [\u0E00-\u0E7F]")
MANUAL_INDENT_BEFORE_THAI = re.compile(r"#h\([^\n)]*\)\s*[\u0E00-\u0E7F]")


def parse_version(text: str) -> tuple[int, ...] | None:
    m = re.search(r"(?:typst\s+)?(\d+)\.(\d+)\.(\d+)", text)
    return tuple(map(int, m.groups())) if m else None


def has_house_import(text: str) -> bool:
    return "thai-worldclass.typ" in text and "thai-worldclass" in text


def static_lint(text: str, document_kind: str) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    thai_present = bool(THAI_RE.search(text))

    for ch, name in [("\u2060", "WORD JOINER U+2060"), ("\u200B", "ZERO WIDTH SPACE U+200B")]:
        if ch in text:
            failures.append(f"{name} found; recompose instead of control-character repair")

    if "\u2009" in text:
        failures.append(
            "U+2009 THIN SPACE found in Typst source; Google Docs renderer adaptation must not leak into the clean semantic source"
        )

    # U+202F/NBSP is allowed only as a protected atom; review rather than reject.
    if "\u202F" in text or "\u00A0" in text:
        warnings.append("NBSP/narrow-NBSP present; verify that each occurrence protects a genuine semantic micro-atom")

    if document_kind == "private" and re.search(r"garuda|ครุฑ", text, re.IGNORECASE):
        failures.append(
            "private-company mode must not inject a Garuda/government-origin emblem merely because the recipient is a government agency"
        )

    house = has_house_import(text)
    compact = re.sub(r"\s+", " ", text)

    # The house module satisfies these deterministic renderer settings by inheritance.
    if thai_present and not house:
        if not re.search(r'lang\s*:\s*"th"', compact):
            failures.append('Thai Typst route must set text lang: "th" or import thai-worldclass.typ')
        if not re.search(r'region\s*:\s*"TH"', compact):
            failures.append('Thai Typst route must set text region: "TH" or import thai-worldclass.typ')
        if not re.search(r'font\s*:', compact):
            failures.append('deterministic Thai Typst output must declare a Thai-capable font priority or import thai-worldclass.typ')

    if re.search(r'justify\s*:\s*true', compact) and not house:
        if not re.search(r'linebreaks\s*:\s*"optimized"', compact):
            failures.append('justified Thai Typst source must explicitly use linebreaks: "optimized" for auditability')
        if "justification-limits" not in compact:
            failures.append('justified Thai Typst source must set conservative justification-limits or import thai-worldclass.typ')

    if MANUAL_INDENT_BEFORE_THAI.search(text):
        failures.append(
            "manual #h(...) indentation before Thai body prose found; use par.first-line-indent instead of geometry text hacks"
        )

    # Repeated spaces in literal Thai prose are usually tab/geometry hacks.
    # Ignore comments and code-dominant lines to reduce false positives.
    thai_ascii_space_count = 0
    thai_chars = len(THAI_RE.findall(text))
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.rstrip("\n")
        if not THAI_RE.search(s):
            continue
        if s.lstrip().startswith("//"):
            continue
        if REPEATED_LAYOUT_SPACE.search(s):
            failures.append(
                f"line {i}: repeated literal spaces appear inside Thai content; use grid/layout primitives instead of space-based tabs or manual wrapping"
            )
        thai_ascii_space_count += len(THAI_TO_THAI_ASCII_SPACE.findall(s))

    # Old typst-govdoc-era manual word separation can look superficially valid.
    # This heuristic intentionally warns rather than fails because Thai semantic breaths
    # may legitimately use ASCII spaces in the clean source.
    if thai_chars >= 120 and thai_ascii_space_count >= max(8, thai_chars // 45):
        warnings.append(
            "high density of Thai-to-Thai ASCII spaces detected; verify they are semantic breath boundaries, not the stale 2023 manual Thai wrapping workaround"
        )

    # Body prose with many explicit hard linebreaks is suspicious; structural address/signature
    # lines are allowed, so this remains a warning.
    hard_break_count = len(re.findall(r"\\\s*$", text, flags=re.MULTILINE))
    thai_lines = sum(1 for line in text.splitlines() if THAI_RE.search(line))
    if thai_lines >= 4 and hard_break_count >= 3:
        warnings.append(
            "multiple explicit Typst hard linebreaks occur in Thai source; verify they are structural (address/signature), not manual body wrapping"
        )

    return failures, warnings


def check_cli() -> tuple[str | None, tuple[int, ...] | None]:
    exe = shutil.which("typst")
    if not exe:
        return None, None
    p = subprocess.run([exe, "--version"], text=True, capture_output=True)
    version = parse_version((p.stdout or "") + " " + (p.stderr or ""))
    return exe, version


def compile_and_check(source: Path, font_path: str | None) -> tuple[int, str]:
    exe, version = check_cli()
    if exe is None:
        return 3, "CANNOT VERIFY: Typst CLI not found in PATH"
    if version is None or version < MIN_VERSION:
        found = ".".join(map(str, version)) if version else "unknown"
        return 3, f"CANNOT VERIFY: Typst >= {'.'.join(map(str, MIN_VERSION))} required; found {found}"

    with tempfile.TemporaryDirectory(prefix="typst-preflight-") as td:
        pdf = Path(td) / "out.pdf"
        cmd = [exe, "compile"]
        if font_path:
            cmd += ["--font-path", font_path]
        cmd += [str(source), str(pdf)]
        p = subprocess.run(cmd, text=True, capture_output=True)
        if p.returncode != 0:
            return 2, "TYPST COMPILE FAIL:\n" + (p.stdout or "") + (p.stderr or "")

        notes = [f"Typst compile PASS ({'.'.join(map(str, version))})"]
        if not pdf.exists() or pdf.stat().st_size == 0:
            return 2, "TYPST COMPILE FAIL: output PDF missing or empty"

        pdftotext = shutil.which("pdftotext")
        if pdftotext:
            txt = Path(td) / "out.txt"
            q = subprocess.run([pdftotext, "-layout", str(pdf), str(txt)], text=True, capture_output=True)
            if q.returncode == 0 and txt.exists():
                rendered = txt.read_text(encoding="utf-8", errors="replace")
                if "\ufffd" in rendered:
                    return 2, "PDF text-integrity FAIL: U+FFFD replacement character found"
                if not rendered.strip():
                    return 2, "PDF text-integrity FAIL: extracted text layer is empty"
                notes.append("pdftotext extraction PASS")
            else:
                notes.append("WARN pdftotext failed; text-layer check not completed")
        else:
            notes.append("WARN pdftotext not installed; text-layer check not completed")

        notes.append("REQUIRED NEXT GATE: rasterize and visually inspect every final PDF page")
        return 0, "\n".join(notes)


def self_test() -> int:
    good = '#import "../thai-worldclass.typ": thai-worldclass\n#show: thai-worldclass\nภาษาไทยเริ่มจากความหมายก่อนการจัดหน้า\n'
    bad_thin = '#import "../thai-worldclass.typ": thai-worldclass\n#show: thai-worldclass\nภาษาไทย\u2009ผิดเส้นทาง\n'
    bad_private = '#import "../thai-worldclass.typ": thai-worldclass\n#show: thai-worldclass\nครุฑ\n'
    bad_indent = '#import "../thai-worldclass.typ": thai-worldclass\n#show: thai-worldclass\n#h(2.5cm)ด้วยบริษัท ตัวอย่าง\n'

    f, _ = static_lint(good, "private")
    if f:
        print("SELF-TEST FAIL: valid house-import sample rejected")
        print("\n".join(f))
        return 2

    f, _ = static_lint(bad_thin, "private")
    if not any("U+2009" in x for x in f):
        print("SELF-TEST FAIL: Google Docs thin-space leak not detected")
        return 2

    f, _ = static_lint(bad_private, "private")
    if not any("Garuda" in x for x in f):
        print("SELF-TEST FAIL: private-mode emblem misuse not detected")
        return 2

    f, _ = static_lint(bad_indent, "private")
    if not any("first-line-indent" in x for x in f):
        print("SELF-TEST FAIL: manual body indent hack not detected")
        return 2

    print("PASS typst_preflight self-test")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", help="Typst .typ source")
    ap.add_argument("--document-kind", choices=["private", "official", "publication"], default="publication")
    ap.add_argument("--compile", action="store_true", help="compile and run PDF text-integrity checks")
    ap.add_argument("--font-path", default=None)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if not args.source:
        ap.error("source is required unless --self-test is used")

    path = Path(args.source)
    text = path.read_text(encoding="utf-8", errors="replace")
    failures, warnings = static_lint(text, args.document_kind)

    for w in warnings:
        print("WARN", w)
    if failures:
        print("TYPST PREFLIGHT FAIL:")
        for f in failures:
            print(" -", f)
        return 2

    print("TYPST STATIC PREFLIGHT PASS")
    if args.compile:
        rc, message = compile_and_check(path, args.font_path)
        print(message)
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
