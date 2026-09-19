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


# Unified paragraph-start ("ขึ้นย่อหน้าใหม่") policy, reconciled 2026-09-19
# across every output format this repo and the merged docs/thai-worldclass/
# pack produce (txt, html, docx here; Typst and LaTeX in
# docs/thai-worldclass/ -- see that pack's thai-worldclass.typ and
# latex/thaiarxiv.sty, both now set to the SAME 2.5cm value). A new
# paragraph is marked by a STRUCTURAL first-line-indent property of the
# output format (docx paragraph_format, HTML CSS text-indent, Typst
# par.first-line-indent, LaTeX \parindent) -- never by inserting a literal
# tab/space character into the text content, per the general principle
# already stated in docs/thai-worldclass/protocols/09-typst.md's
# "Grid-not-spaces rule" and consistent with KNOWN_ISSUES.md ISSUE 1 (don't
# fix Thai text problems by injecting characters into content).
#
# The ONE justified exception is plain .txt: it has no structural styling
# concept at all, so there is no way to express "first-line indent" other
# than a literal character. For that one format only, a single leading TAB
# is used per body paragraph -- chosen (not an arbitrary pick) to match
# what gov-templates/NIA's real official templates actually do (verified:
# their body paragraphs start with a literal \t, not spaces or a dot
# leader) rather than inventing a different plain-text convention.
#
# TITLE (and any other non-body section a caller may add) is excluded from
# indentation -- it is a heading, not body prose.
BODY_FIRST_LINE_INDENT_CM = 2.5
NON_BODY_SECTIONS = {"_preamble", "TITLE"}


def write_txt(sections: dict[str, str], out_path: pathlib.Path) -> None:
    parts = []
    for name, text in sections.items():
        if name != "_preamble":
            parts.append(f"#{name}#")
        if name in NON_BODY_SECTIONS:
            parts.append(text)
        else:
            # One leading tab per paragraph -- the plain-text-only exception
            # described above. Paragraphs are joined with a SINGLE newline,
            # not a blank line: the indent alone marks a new paragraph, so a
            # blank-line gap on top of it would double up two different
            # "new paragraph" signals and read as one line of dead space too
            # many (founder correction 2026-09-19: "เว้นเกินไปหนึ่งบรรทัด" --
            # spaced one line too much). This matches the same "indent, not
            # gap" policy already applied to docx/html below and to Typst/
            # LaTeX in docs/thai-worldclass/ -- one convention, everywhere.
            # .strip() each fragment (not just filter on it) -- a source
            # text with a "\n\n\n" gap (e.g. a Jinja2 template with a blank
            # line already between two {{ vars }} that are themselves
            # separated by another blank template line) otherwise leaves a
            # stray leading "\n" inside the fragment, landing the tab on an
            # empty line instead of the real paragraph text (adversarial
            # review finding 2026-09-19, confirmed against this exact
            # template+data pair; write_docx already did this correctly via
            # para.strip(), this brings write_txt/write_html in line with it).
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            parts.append("\n".join("\t" + p for p in paras))
        parts.append("")
    out_path.write_text("\n".join(parts), encoding="utf-8")


def write_html(sections: dict[str, str], out_path: pathlib.Path, title: str = "") -> None:
    # lang="th" + a Thai-safe font stack. No ZWSP/space patching is applied
    # here (see module docstring / ../KNOWN_ISSUES.md ISSUE 1); real line-fit
    # problems belong to the source text's composition, not this renderer.
    # Body paragraphs get a structural CSS text-indent (see policy note
    # above); TITLE does not. Paragraph gap is intentionally near-zero
    # (margin: 0 0 0.15em) to match the "first-line indent + zero/restrained
    # extra gap" convention docs/thai-worldclass/protocols/04-docx-pdf.md
    # specifies -- indent and gap are not meant to be doubled up.
    body_html = []
    for name, text in sections.items():
        if name == "_preamble":
            continue
        is_body = name not in NON_BODY_SECTIONS
        # .strip() each fragment -- see the matching comment in write_txt;
        # without it a "\n\n\n" source gap leaves a stray leading newline
        # inside the <p> tag.
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        body_html.append(f'<section data-name="{name}">')
        for p in paragraphs:
            escaped = (
                p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            cls = ' class="body-p"' if is_body else ""
            body_html.append(f"<p{cls}>{escaped}</p>")
        body_html.append("</section>")
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: "Noto Sans Thai", "TH Sarabun New", sans-serif; line-height: 1.6; }}
p {{ word-break: normal; overflow-wrap: break-word; margin: 0 0 0.15em; }}
p.body-p {{ text-indent: {BODY_FIRST_LINE_INDENT_CM}cm; }}
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
    from docx.shared import Cm, Pt

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
        if name in NON_BODY_SECTIONS:
            continue
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                p = doc.add_paragraph(para)
                # Structural first-line indent (see the policy note above
                # write_txt) -- never a literal leading tab/space in the
                # text content. Zero extra paragraph gap: indent and gap
                # are not doubled up (matches
                # docs/thai-worldclass/protocols/04-docx-pdf.md).
                p.paragraph_format.first_line_indent = Cm(BODY_FIRST_LINE_INDENT_CM)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.space_before = Pt(0)

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
