#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "SKILL.md", "agents/openai.yaml", "assets/preview.png", "manifest.txt",
    "README.md", "INSTALL.md", "BUILD_REPORT.md", "VERSION",
    "RESEARCH_NOTES_TYPST_2.1.md",
    "protocols/00-routing.md",
    "protocols/01-thai-semantic-breathing.md",
    "protocols/02-overflow-and-qa.md",
    "protocols/03-google-docs.md",
    "protocols/04-docx-pdf.md",
    "protocols/05-latex-arxiv.md",
    "protocols/06-style-a.md",
    "protocols/07-style-c.md",
    "protocols/08-release-checklist.md",
    "protocols/09-typst.md",
    "scripts/thai_semantic_lint.py",
    "scripts/typst_preflight.py",
    "latex/examples/A_worldclass_onecolumn.tex",
    "latex/examples/C_worldclass_twocolumn.tex",
    "latex/examples/A_worldclass_onecolumn.pdf",
    "latex/examples/C_worldclass_twocolumn.pdf",
    "latex/thaiarxiv.sty",
    "latex/tools/preflight.py",
    "latex/tools/source_lint.py",
    "latex/tools/make_arxiv_zip.py",
    "latex/tools/run_regression.py",
    "typst/thai-worldclass.typ",
    "typst/formal-letter.typ",
    "typst/examples/formal_private_to_government.typ",
    "typst/tests/good_clean_thai.typ",
    "typst/tests/bad_google_docs_leak.typ",
]
missing = [p for p in required if not (root / p).is_file()]
if missing:
    print("FAIL missing:")
    print("\n".join(missing))
    sys.exit(2)

version = (root / "VERSION").read_text().strip()
if version != "2.1.0":
    print(f"FAIL VERSION must be 2.1.0; got {version!r}")
    sys.exit(2)

checks = {
    "SKILL.md": [
        "CRITICAL — KNOWN AI FAILURE MODES",
        "HARD EXECUTION CONTRACT",
        "Spacing MUST follow thought",
        "Mandatory stop conditions",
        "Alignment-escape failure",
        "Mixed-script stretch failure",
        "Latin-run exemption failure",
        "Stale-reference failure",
        "Cross-render contamination failure",
        "Authority-emblem failure",
        "Compositor-as-semantics failure",
        "protocols/09-typst.md",
        "Typst >=0.15.1",
    ],
    "protocols/01-thai-semantic-breathing.md": [
        "Meaning → Thought Unit → Breath Weight → Rhythm Variation → Line Fit → Rendering Separator",
        "Lookahead rule is mandatory",
        "THIN SPACE U+2009",
        "WORD JOINER",
        "Spacing must follow thought",
    ],
    "protocols/03-google-docs.md": [
        "Strict Thai Enforcement",
        "Ordinary U+0020",
        "Forbidden repair behavior",
        "Mechanical lint",
        "fail closed",
        "NO safety default",
        "alignment-escape failure",
        "Mixed-script",
        "no purely-Latin-run exemption",
        "Typst comparison render (v2.1)",
    ],
    "protocols/08-release-checklist.md": [
        "Execution proof",
        "Thai semantic composition",
        "For Typst:",
        "Typst >=0.15.1",
        "Mandatory status language",
        "CANNOT VERIFY",
    ],
    "protocols/09-typst.md": [
        "Typst Route — Thai Layout Oracle and Final PDF Compositor (v2.1)",
        "LineSegmenter::new_lstm",
        "linebreaks: \"optimized\"",
        "justification-limits",
        "clean semantic source",
        "private-formal",
        "do not insert the Garuda emblem",
        "first-line-indent",
        "CANNOT VERIFY",
    ],
    "RESEARCH_NOTES_TYPST_2.1.md": [
        "b0ca4535c92f70aa94ace3f9bcffeae501df893b",
        "094b9634d2aa506757d342103411a33a347e3012",
        "v0.15.1",
        "ICU4X",
        "Apache-2.0",
        "No file from `typst-govdoc` is bundled verbatim",
    ],
}
for rel, needles in checks.items():
    text = (root / rel).read_text(encoding="utf-8")
    missing_needles = [n for n in needles if n not in text]
    if missing_needles:
        print(f"FAIL enforcement/research contract missing from {rel}:")
        for n in missing_needles:
            print(" -", n)
        sys.exit(2)

# Alignment policy must not contain active START/LEFT safety defaults or fallbacks.
alignment_files = [root / "SKILL.md", root / "protocols" / "00-routing.md", root / "protocols" / "03-google-docs.md"]
for f in alignment_files:
    text = f.read_text(encoding="utf-8")
    forbidden = [
        "Use START alignment by default",
        "route to START alignment",
        "fail closed to START alignment",
        "START is the safe collaboration default",
    ]
    hits = [x for x in forbidden if x in text]
    if hits:
        print(f"FAIL active START/LEFT safety fallback remains in {f.relative_to(root)}:")
        for h in hits:
            print(" -", h)
        sys.exit(2)

# v2.1 private-formal package must not bundle a Garuda asset.
for p in root.rglob("*"):
    if p.is_file() and "garuda" in p.name.lower():
        print(f"FAIL government-origin emblem asset bundled unexpectedly: {p.relative_to(root)}")
        sys.exit(2)

# Discarded profiles must not leak into filenames.
bad_names = [
    p for p in root.rglob("*")
    if p.is_file() and any(x in p.name.lower() for x in ["style_b", "style_d", "profile_b", "profile_d"])
]
if bad_names:
    print("FAIL discarded profile artifacts found:")
    print("\n".join(str(p.relative_to(root)) for p in bad_names))
    sys.exit(2)

# Mechanical Thai linter self-test.
lint = root / "scripts" / "thai_semantic_lint.py"
proc = subprocess.run([sys.executable, str(lint), "--self-test"], text=True, capture_output=True)
print(proc.stdout, end="")
if proc.returncode != 0:
    print(proc.stderr, end="")
    print("FAIL thai_semantic_lint self-test")
    sys.exit(2)

# Typst preflight must prove clean-route and negative-route behavior.
typst_lint = root / "scripts" / "typst_preflight.py"
proc = subprocess.run([sys.executable, str(typst_lint), "--self-test"], text=True, capture_output=True)
print(proc.stdout, end="")
if proc.returncode != 0:
    print(proc.stderr, end="")
    print("FAIL typst_preflight self-test")
    sys.exit(2)

for rel, kind in [
    ("typst/tests/good_clean_thai.typ", "publication"),
    ("typst/examples/formal_private_to_government.typ", "private"),
]:
    proc = subprocess.run(
        [sys.executable, str(typst_lint), str(root / rel), "--document-kind", kind],
        text=True, capture_output=True,
    )
    print(proc.stdout, end="")
    if proc.returncode != 0:
        print(proc.stderr, end="")
        print(f"FAIL Typst static preflight on {rel}")
        sys.exit(2)

proc = subprocess.run(
    [sys.executable, str(typst_lint), str(root / "typst/tests/bad_google_docs_leak.typ"), "--document-kind", "publication"],
    text=True, capture_output=True,
)
if proc.returncode == 0:
    print("FAIL negative Typst regression: Google Docs U+2009 leak was accepted")
    sys.exit(2)
print("PASS negative Typst regression rejected Google Docs U+2009 leak")

# Live Typst compile is opportunistic at package-build time. Runtime final verification
# remains fail-closed if the CLI is unavailable.
if shutil.which("typst"):
    proc = subprocess.run(
        [sys.executable, str(typst_lint), str(root / "typst/examples/formal_private_to_government.typ"),
         "--document-kind", "private", "--compile"],
        text=True, capture_output=True,
    )
    print(proc.stdout, end="")
    if proc.returncode != 0:
        print(proc.stderr, end="")
        print("FAIL live Typst compile/preflight")
        sys.exit(2)
else:
    print("SKIP live Typst compile: CLI unavailable; runtime final Typst verification remains CANNOT VERIFY")

# Manifest must exactly describe the packaged tree. Do this last so the build report
# and all route files are included in the check.
manifest_path = root / "manifest.txt"
manifest = [x.strip() for x in manifest_path.read_text(encoding="utf-8").splitlines() if x.strip()]
actual = sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file())
if sorted(manifest) != actual:
    print("FAIL manifest.txt does not match packaged files")
    missing_from_manifest = sorted(set(actual) - set(manifest))
    stale_in_manifest = sorted(set(manifest) - set(actual))
    if missing_from_manifest:
        print("Missing from manifest:")
        for x in missing_from_manifest:
            print(" -", x)
    if stale_in_manifest:
        print("Stale manifest entries:")
        for x in stale_in_manifest:
            print(" -", x)
    sys.exit(2)

print("PASS standalone pack structure + strict Thai enforcement + Typst v2.1 contract")
