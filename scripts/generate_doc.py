"""
generate_doc.py -- fill a template with data and emit a Thai document in
one of: plain text, HTML, or .docx.

CHANGED (see ../KNOWN_ISSUES.md "ISSUE 1"): this script used to run every
Thai text field through thai_linebreak.fix_thai_linebreaks (blanket ZWSP
insertion between all dictionary-tokenized words) before writing output.
That approach is demoted -- it does not fix the failure mode that actually
dominates in practice (Google Docs JUSTIFIED Thai stretching ordinary
spaces) and it can split genuine semantic wholes. This script no longer
applies that fix by default.

What it does instead: renders the template as authored, then runs the
merged `docs/thai-worldclass/scripts/thai_semantic_lint.py` mechanical
gate (via --lint) against the final text and REPORTS findings rather than
silently patching them. Real Thai line-wrap/rhythm problems must be fixed
by recomposing the source text (see docs/thai-worldclass/SKILL.md), not by
inserting control characters after the fact -- this script deliberately
does not do that for you.

Design goal: the SAME data + SAME template must produce byte-identical text
content across every output format (only the container differs).

Template format
----------------
A template is a Jinja2 text file (see templates/*.txt.j2) whose rendered
output is plain text with simple block markers:

    #TITLE#
    <title text>

    #BODY#
    <one or more paragraphs, blank line = new paragraph>

generate_doc.py renders the Jinja2 template against the data file first
(so {{ placeholders }} are substituted), THEN parses the #TITLE#/#BODY#
markers, THEN (optionally, with --lint) runs the mechanical Thai lint gate,
THEN writes the requested output format.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

import yaml
from jinja2 import Template

_REPO_ROOT = pathlib.Path(__file__).parent.parent
_LINT_SCRIPT = _REPO_ROOT / "docs" / "thai-worldclass" / "scripts" / "thai_semantic_lint.py"


def load_data(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    if path.suffix == ".json":
        return json.loads(text)
    raise ValueError(f"Unsupported data file type: {path.suffix} (use .yaml or .json)")


def render_template(template_path: pathlib.Path, data: dict) -> str:
    tmpl = Template(template_path.read_text(encoding="utf-8"))
    return tmpl.render(**data)


def parse_sections(rendered: str) -> dict[str, str]:
    """Split a rendered template into named sections on '#NAME#' marker
    lines. Returns {section_name: section_text}. Text before the first
    marker (if any) is stored under section name '_preamble'."""
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for line in rendered.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#") and stripped.endswith("#") and len(stripped) > 2:
            current = stripped.strip("#").strip()
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return {name: "\n".join(lines).strip("\n") for name, lines in sections.items()}


def lint_sections(sections: dict[str, str], mode: str = "google-docs-justified") -> bool:
    """Run the merged docs/thai-worldclass mechanical lint against the final
    rendered text and print its findings. Returns True iff lint passed for
    every section. This is a REPORT-ONLY gate -- on failure it tells the
    caller what to recompose; it never auto-patches the text (see
    ../KNOWN_ISSUES.md "ISSUE 1" for why auto-patching was the mistake)."""
    if not _LINT_SCRIPT.exists():
        print(f"warning: lint script not found at {_LINT_SCRIPT}, skipping", file=sys.stderr)
        return True
    import tempfile

    all_ok = True
    for name, text in sections.items():
        if not text.strip():
            continue
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(text)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [sys.executable, str(_LINT_SCRIPT), tmp_path, "--mode", mode],
                capture_output=True,
                text=True,
            )
        finally:
            pathlib.Path(tmp_path).unlink(missing_ok=True)
        if result.returncode != 0:
            all_ok = False
            print(f"--- lint findings in section '{name}' ---", file=sys.stderr)
            print(result.stdout or result.stderr, file=sys.stderr)
    return all_ok


def write_txt(sections: dict[str, str], out_path: pathlib.Path) -> None:
    parts = []
    for name, text in sections.items():
        if name != "_preamble":
            parts.append(f"#{name}#")
        parts.append(text)
        parts.append("")
    out_path.write_text("\n".join(parts), encoding="utf-8")


def write_html(sections: dict[str, str], out_path: pathlib.Path, title: str = "") -> None:
    # lang="th" + a Thai-safe font stack. No ZWSP/space patching is applied
    # here (see module docstring / ../KNOWN_ISSUES.md ISSUE 1); real line-fit
    # problems belong to the source text's composition, not this renderer.
    body_html = []
    for name, text in sections.items():
        if name == "_preamble":
            continue
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        body_html.append(f'<section data-name="{name}">')
        for p in paragraphs:
            escaped = (
                p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            body_html.append(f"<p>{escaped}</p>")
        body_html.append("</section>")
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: "Noto Sans Thai", "TH Sarabun New", sans-serif; line-height: 1.6; }}
p {{ word-break: normal; overflow-wrap: break-word; }}
</style>
</head>
<body>
{chr(10).join(body_html)}
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")


def write_docx(sections: dict[str, str], out_path: pathlib.Path, font_name: str = "TH Sarabun New") -> None:
    import docx
    from docx.shared import Pt

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = font_name
    style.font.size = Pt(16)
    # Thai text needs the East-Asian/complex-script font slot set too, or
    # some Office builds silently fall back to a Latin default font for the
    # Thai glyph run even though style.font.name looks correct.
    #
    # NOTE: `style.font.name = font_name` above already creates a w:rFonts
    # element (with only w:ascii/w:hAnsi set) as a side effect of
    # python-docx's Font.name setter, so `rfonts` is essentially never None
    # by the time we get here. The eastAsia/cs attributes must therefore be
    # set unconditionally on whatever element we find-or-create, not only
    # inside a "just created it" branch -- setting them only when creating a
    # brand-new element would silently never run in practice.
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), font_name)
    rfonts.set(qn("w:hAnsi"), font_name)
    rfonts.set(qn("w:eastAsia"), font_name)
    rfonts.set(qn("w:cs"), font_name)

    if "TITLE" in sections and sections["TITLE"]:
        heading = doc.add_heading(level=0)
        heading.add_run(sections["TITLE"])

    for name, text in sections.items():
        if name in ("_preamble", "TITLE"):
            continue
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                doc.add_paragraph(para)

    doc.save(str(out_path))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("template", type=pathlib.Path, help="Jinja2 template file (see templates/)")
    ap.add_argument("data", type=pathlib.Path, help="Data file (.yaml or .json)")
    ap.add_argument("-o", "--out", type=pathlib.Path, required=True, help="Output file path")
    ap.add_argument(
        "-f", "--format", choices=["txt", "html", "docx"], required=True, help="Output format"
    )
    ap.add_argument("--font", default="TH Sarabun New", help="Font for docx output")
    ap.add_argument(
        "--lint",
        action="store_true",
        help="run docs/thai-worldclass mechanical Thai lint on the rendered "
        "text and report findings (does not modify output)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="with --lint, exit non-zero (and still write output) if lint finds hard failures",
    )
    args = ap.parse_args()

    data = load_data(args.data)
    rendered = render_template(args.template, data)
    sections = parse_sections(rendered)

    lint_ok = True
    if args.lint:
        lint_ok = lint_sections(sections)
        if lint_ok:
            print("thai_semantic_lint: PASS (mechanical gate only -- see docs/thai-worldclass/SKILL.md)")

    if args.format == "txt":
        write_txt(sections, args.out)
    elif args.format == "html":
        write_html(sections, args.out, title=sections.get("TITLE", ""))
    elif args.format == "docx":
        write_docx(sections, args.out, font_name=args.font)

    print(f"wrote {args.out} ({args.format})")
    if args.strict and not lint_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
