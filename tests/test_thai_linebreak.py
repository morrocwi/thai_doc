import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "scripts"))

from thai_linebreak import ZWSP, fix_thai_linebreaks, strip_zwsp  # noqa: E402


def test_round_trip_loses_nothing():
    text = "สวัสดีครับวันนี้อากาศดีมากเหมาะแก่การทำงาน"
    fixed = fix_thai_linebreaks(text)
    assert strip_zwsp(fixed) == text


def test_inserts_zwsp_between_thai_words():
    text = "ประเทศไทยมีความสวยงาม"
    fixed = fix_thai_linebreaks(text)
    assert ZWSP in fixed


def test_idempotent():
    text = "การศึกษาไทยกำลังพัฒนาอย่างต่อเนื่อง"
    once = fix_thai_linebreaks(text)
    twice = fix_thai_linebreaks(once)
    assert once == twice


def test_preserves_existing_whitespace_and_newlines():
    text = "บรรทัดที่หนึ่ง\nบรรทัดที่สอง มีช่องว่าง"
    fixed = fix_thai_linebreaks(text)
    assert "\n" in fixed
    assert strip_zwsp(fixed) == text


def test_leaves_latin_and_numbers_untouched():
    text = "ราคา 1500 บาท สำหรับ COVID-19 test"
    fixed = fix_thai_linebreaks(text)
    assert "COVID-19" in fixed
    assert "1500" in fixed


def test_empty_string():
    assert fix_thai_linebreaks("") == ""


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
