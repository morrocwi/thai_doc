#!/usr/bin/env python3
"""
aick_generate.py -- structured-data-in / rendered-.tex-out generator for
the Center for AI Civic Knowledge Thai preprint house class
(org-templates/AICK/source/aick-thai-preprint.cls).

Mirrors this repo's own existing pattern at scripts/generate_doc.py +
templates/formal_letter.txt.j2 + examples/formal_letter.example.yaml:
a Jinja2 template is rendered against a YAML/JSON data file, producing
the final document (here: a .tex file matching the shape of
org-templates/AICK/source/aick-paper-template.tex).

Validation: the data file is checked against
org-templates/AICK/schema/aick_paper.schema.json first, using the
`jsonschema` library when available, else a hand-rolled required-field/
type check that enforces the same required fields and the `sections`
array shape.

Usage
-----
    python3 aick_generate.py <data.yaml|data.json> -o <out.tex>

Does NOT modify aick-thai-preprint.cls or aick-paper-template.tex --
this script only ever reads them (indirectly, via the schema/template
that describe their API) and writes a new .tex file at -o/--out.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

_HERE = pathlib.Path(__file__).parent
_AICK_ROOT = _HERE.parent
_SCHEMA_PATH = _AICK_ROOT / "schema" / "aick_paper.schema.json"
_TEMPLATE_DIR = _AICK_ROOT / "templates"
_TEMPLATE_NAME = "aick_paper.tex.j2"

_REQUIRED_STRING_FIELDS = [
    "title",
    "subtitle",
    "author",
    "authorshort",
    "orcid",
    "affiliation",
    "shorttitle",
    "version",
    "date",
    "abstract",
    "keywords",
    "methodology_note",
]


def load_data(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    if path.suffix == ".json":
        return json.loads(text)
    raise ValueError(f"Unsupported data file type: {path.suffix} (use .yaml or .json)")


def validate_with_jsonschema(data: dict, schema: dict) -> list[str]:
    import jsonschema

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


def validate_hand_rolled(data: dict) -> list[str]:
    """Fallback validation used only if the `jsonschema` library is not
    installed. Enforces the same required fields and shapes as
    schema/aick_paper.schema.json, hand-rolled."""
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["<root>: data file must be a mapping/object"]

    for field in _REQUIRED_STRING_FIELDS:
        if field not in data:
            errors.append(f"{field}: required field is missing")
        elif not isinstance(data[field], str):
            errors.append(f"{field}: must be a string")

    if "sections" not in data:
        errors.append("sections: required field is missing")
    else:
        sections = data["sections"]
        if not isinstance(sections, list) or len(sections) < 1:
            errors.append("sections: must be a non-empty array")
        else:
            for i, sec in enumerate(sections):
                if not isinstance(sec, dict):
                    errors.append(f"sections/{i}: must be an object")
                    continue
                for key in ("heading", "body"):
                    if key not in sec:
                        errors.append(f"sections/{i}/{key}: required field is missing")
                    elif not isinstance(sec[key], str):
                        errors.append(f"sections/{i}/{key}: must be a string")

    for field in ("acknowledgements", "declarations"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"{field}: must be a string")

    if "references" in data:
        refs = data["references"]
        if not isinstance(refs, list):
            errors.append("references: must be an array")
        else:
            for i, ref in enumerate(refs):
                if not isinstance(ref, str):
                    errors.append(f"references/{i}: must be a string")

    extra_keys = set(data.keys()) - set(_REQUIRED_STRING_FIELDS) - {
        "sections",
        "acknowledgements",
        "declarations",
        "references",
    }
    if extra_keys:
        errors.append(f"<root>: unexpected extra field(s): {sorted(extra_keys)}")

    return errors


def validate(data: dict) -> list[str]:
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        print(
            "note: `jsonschema` library not available, falling back to "
            "hand-rolled required-field check",
            file=sys.stderr,
        )
        return validate_hand_rolled(data)

    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_with_jsonschema(data, schema)


def render(data: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template(_TEMPLATE_NAME)
    render_data = dict(data)
    render_data.setdefault("acknowledgements", "")
    render_data.setdefault("declarations", "")
    render_data.setdefault("references", [])
    return template.render(**render_data)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data", type=pathlib.Path, help="Data file (.yaml or .json)")
    ap.add_argument("-o", "--out", type=pathlib.Path, required=True, help="Output .tex path")
    args = ap.parse_args()

    data = load_data(args.data)

    errors = validate(data)
    if errors:
        print("aick_paper.schema.json validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("schema validation: PASS")

    rendered = render(data)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
