#!/usr/bin/env python3
"""Strict XeLaTeX/arXiv preflight for Thai scientific papers.

The script treats layout overflow, unresolved cross-references, missing glyphs,
font embedding/ToUnicode failures, and suspicious Thai text-layer loss as build
failures. Underfull boxes and controlled last-resort scaling remain warnings.
"""
import argparse
import pathlib
import re
import subprocess
import sys
import unicodedata

OVERFULL_H = re.compile(r"Overfull \\hbox \(([-0-9.]+)pt too wide\)")
OVERFULL_V = re.compile(r"Overfull \\vbox \(([-0-9.]+)pt too high\)")

FATAL_REGEX = [
    (re.compile(r"TA-EQ-SEVERE"), "severe equation scaling"),
    (re.compile(r"TA-TABLE-SEVERE"), "severe table scaling"),
    (re.compile(r"LaTeX Warning: There were undefined references"), "undefined references"),
    (re.compile(r"LaTeX Warning: Reference .* undefined"), "undefined reference"),
    (re.compile(r"(?:LaTeX|Package natbib) Warning: Citation .* undefined"), "undefined citation"),
    (re.compile(r"Missing character:"), "missing glyph"),
]
WARN_REGEX = [
    (re.compile(r"TA-EQ-SCALED"), "equation scaled"),
    (re.compile(r"TA-TABLE-SCALED"), "table scaled"),
    (re.compile(r"Underfull \\hbox"), "underfull hbox"),
    (re.compile(r"Underfull \\vbox"), "underfull vbox"),
]

THAI_RE = re.compile(r"[\u0E00-\u0E7F]")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def suspicious_thai_combining(text):
    bad = []
    prev = ""
    for i, ch in enumerate(text):
        if unicodedata.combining(ch):
            if not prev or prev.isspace() or unicodedata.category(prev)[0] in "PZ":
                bad.append((i, ch))
        prev = ch
    return bad


def strip_tex_comments(source):
    lines = []
    for line in source.splitlines():
        # Remove unescaped % comments; this is deliberately conservative.
        m = re.search(r"(?<!\\)%", line)
        if m:
            line = line[:m.start()]
        lines.append(line)
    return "\n".join(lines)


def thai_count(s):
    return len(THAI_RE.findall(unicodedata.normalize("NFC", s)))


def inspect_pdffonts(pdf, cwd):
    failures = []
    out = run(["pdffonts", str(pdf)], cwd)
    if out.returncode != 0:
        return ["pdffonts could not inspect PDF"]
    for line in out.stdout.splitlines()[2:]:
        if not line.strip():
            continue
        # pdffonts ends with: emb sub uni object-ID generation
        m = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line, flags=re.I)
        if not m:
            continue
        emb, _sub, uni = (x.lower() for x in m.groups())
        font_name = line.split()[0]
        if emb != "yes":
            failures.append(f"unembedded font: {font_name}")
        if uni != "yes":
            failures.append(f"font lacks ToUnicode map: {font_name}")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--overfull-limit", type=float, default=1.0,
                    help="fail if an overfull box exceeds this many pt (default: 1.0)")
    ap.add_argument("--thai-text-ratio", type=float, default=0.90,
                    help="minimum extracted/source Thai codepoint ratio (default: 0.90)")
    args = ap.parse_args()

    tex = pathlib.Path(args.tex).resolve()
    cwd = tex.parent
    base = tex.stem

    build = run(["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd)
    print(build.stdout)

    failures, warnings = [], []
    if build.returncode != 0:
        failures.append(f"latexmk failed with exit code {build.returncode}")

    log = cwd / f"{base}.log"
    if not log.exists():
        failures.append("no log produced")
        log_text = ""
    else:
        log_text = log.read_text(errors="replace")

    for rx, label in FATAL_REGEX:
        if rx.search(log_text):
            failures.append(label)
    for rx, label in WARN_REGEX:
        if rx.search(log_text):
            warnings.append(label)

    for rx, label in [(OVERFULL_H, "overfull hbox"), (OVERFULL_V, "overfull vbox")]:
        for m in rx.finditer(log_text):
            try:
                amount = float(m.group(1))
            except ValueError:
                amount = 999.0
            if amount > args.overfull_limit:
                failures.append(f"{label}: {amount:.3f}pt")

    pdf = cwd / f"{base}.pdf"
    if not pdf.exists():
        failures.append("PDF not produced")
    else:
        info = run(["pdfinfo", str(pdf)], cwd)
        if info.returncode != 0:
            failures.append("pdfinfo could not read PDF")
        failures.extend(inspect_pdffonts(pdf, cwd))

        txt = cwd / f"{base}.preflight.txt"
        extract = run(["pdftotext", "-enc", "UTF-8", str(pdf), str(txt)], cwd)
        if extract.returncode != 0 or not txt.exists():
            failures.append("pdftotext could not extract PDF text")
        else:
            extracted = txt.read_text(errors="replace")
            if "\ufffd" in extracted:
                failures.append("replacement character U+FFFD in extracted PDF text")
            bad = suspicious_thai_combining(extracted)
            if bad:
                warnings.append(f"{len(bad)} suspicious combining marks at whitespace/punctuation boundaries")

            source = strip_tex_comments(tex.read_text(errors="replace"))
            src_thai = thai_count(source)
            pdf_thai = thai_count(extracted)
            if src_thai >= 40:
                ratio = pdf_thai / src_thai
                print(f"THAI-TEXT-LAYER: source={src_thai} extracted={pdf_thai} ratio={ratio:.3f}")
                if ratio < args.thai_text_ratio:
                    failures.append(
                        f"Thai PDF text-layer coverage too low: {ratio:.3f} < {args.thai_text_ratio:.3f}"
                    )

    if warnings:
        print("PRECHECK WARN:")
        for w in sorted(set(warnings)):
            print(" -", w)
    if failures:
        print("PRECHECK FAIL:")
        for f in sorted(set(failures)):
            print(" -", f)
        return 2

    print("PRECHECK PASS: compile, overflow, references, fonts, ToUnicode, and Thai text-layer gates passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
