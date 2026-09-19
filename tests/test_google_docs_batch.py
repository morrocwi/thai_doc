import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from google_docs_batch import (  # noqa: E402
    build_requests_from_lock,
    build_requests_from_sections,
    utf16_len,
)


def test_utf16_len_ascii():
    assert utf16_len("hello") == 5


def test_utf16_len_thai_combining_marks():
    # ่ = mai ek (tone mark), ้ = mai tho -- both combine with a
    # preceding consonant but are each their own Unicode codepoint AND each
    # a single UTF-16 code unit (within the BMP). Confirms utf16_len counts
    # each combining mark as +1, matching what the Google Docs API actually
    # counts, not silently dropping/merging them.
    s = "ก่าง"  # ก่าง : consonant + tone mark + vowel + consonant
    assert len(s) == 4
    assert utf16_len(s) == 4  # all BMP -> Python len() and UTF-16 code-unit count agree here


def test_utf16_len_surrogate_pair():
    # U+1F600 (an emoji, outside the BMP) encodes as a UTF-16 SURROGATE
    # PAIR -- 2 code units -- even though Python's len() counts it as ONE
    # character. This is exactly the case that makes plain len() wrong for
    # Google Docs indices, and the reason this module never uses it.
    s = "\U0001f600"
    assert len(s) == 1
    assert utf16_len(s) == 2


def test_build_requests_from_sections_index_monotonic_and_nonoverlapping():
    sections = {"TITLE": "หัวข้อ", "BODY": "ย่อหน้าแรก มีเนื้อหา\n\nย่อหน้าที่สอง"}
    reqs = build_requests_from_sections(sections)
    # Every insertText's index must equal the running end of all previous
    # insertions (monotonic, no gaps, no overlaps).
    expected_index = 1
    for r in reqs:
        if "insertText" in r:
            assert r["insertText"]["location"]["index"] == expected_index
            expected_index += utf16_len(r["insertText"]["text"])
        elif "updateParagraphStyle" in r:
            rng = r["updateParagraphStyle"]["range"]
            assert rng["endIndex"] == expected_index


def test_build_requests_from_sections_title_excluded_from_indent():
    sections = {"TITLE": "หัวข้อ", "BODY": "เนื้อหา"}
    reqs = build_requests_from_sections(sections)
    style_reqs = [r["updateParagraphStyle"] for r in reqs if "updateParagraphStyle" in r]
    assert not style_reqs[0]["paragraphStyle"].get("indentFirstLine")  # TITLE
    assert style_reqs[1]["paragraphStyle"]["indentFirstLine"]["magnitude"] == 2.5  # BODY


def test_build_requests_from_lock_fills_and_self_checks():
    lock = {
        "source_file": "t.docx",
        "paragraphs": [
            [
                {"type": "fixed", "text": "เรื่อง ", "boundary_left": True},
                {"type": "placeholder", "raw": "....(หัวข้อ)....", "label": "หัวข้อ"},
            ]
        ],
    }
    reqs, flattened = build_requests_from_lock(lock, {"หัวข้อ": "การทดสอบ"})
    assert "เรื่อง การทดสอบ" in flattened
    assert any("insertText" in r for r in reqs)


def test_build_requests_from_lock_refuses_missing_value():
    lock = {
        "source_file": "t.docx",
        "paragraphs": [
            [
                {"type": "fixed", "text": "เรื่อง "},
                {"type": "placeholder", "raw": "....(หัวข้อ)....", "label": "หัวข้อ"},
            ]
        ],
    }
    try:
        build_requests_from_lock(lock, {})
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_build_requests_from_lock_fills_unlabeled_placeholder_by_id():
    # Regression test for the 2026-09-19 fix: a placeholder with no inline
    # (label) -- e.g. a bare date blank, common in every real NIA letter --
    # must still be fillable, via its stable "id", not just a labeled one.
    lock = {
        "source_file": "t.docx",
        "paragraphs": [
            [
                {"type": "fixed", "text": "วันที่ ", "boundary_left": True},
                {"type": "placeholder", "raw": "..........", "label": None, "id": "ph0"},
            ]
        ],
    }
    # No label exists for this placeholder -- the OLD code could never
    # satisfy it under any values dict. Confirm it fails without the id...
    try:
        build_requests_from_lock(lock, {"some_other_key": "x"})
        assert False, "expected ValueError for an unaddressed unlabeled placeholder"
    except ValueError:
        pass
    # ...and succeeds when addressed by its id.
    reqs, flattened = build_requests_from_lock(lock, {"ph0": "19 กันยายน 2569"})
    assert "วันที่ 19 กันยายน 2569" in flattened
    assert any("insertText" in r for r in reqs)


if __name__ == "__main__":
    import inspect

    mod = sys.modules[__name__]
    failures = 0
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
