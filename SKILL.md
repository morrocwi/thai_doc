---
name: thai_doc
description: Load before generating or fixing any Thai-language document meant to be pasted or opened in an external tool (desktop apps, Google Docs, Word, a browser, a PDF viewer). Fixes the "ตัดบรรทัดไม่ได้" problem (Thai has no inter-word spaces, so layout engines overflow or break mid-word) by inserting dictionary-segmented zero-width spaces, and generates template-accurate Thai documents (txt/html/docx) from a Jinja2 template + data file. Trigger on: "พิมพ์ภาษาไทย", "ตัดบรรทัดภาษาไทย", "ตัดคำภาษาไทยไม่ได้", "สร้างเอกสารภาษาไทยตามเทมเพลท", "paste Thai text into Google Docs/Word", any request to generate a Thai-language letter/certificate/form from a template.
---

# thai_doc

Public repo: https://github.com/morrocwi/thai_doc (MIT license, code only).

## When to use this

- Someone needs Thai text that will be pasted into Google Docs, Word, a chat
  box, or any tool whose line-wrapping mangles long Thai runs.
- Someone needs a Thai document (letter, certificate, form, ...) generated
  accurately from a template + data, in txt/html/docx.

## How to use it

1. Fixing a block of Thai text for pasting elsewhere:
   ```
   python3 <repo>/scripts/thai_linebreak.py "<Thai text>"
   ```
   The output is byte-identical to the input except for inserted U+200B
   (zero-width space) characters at real word boundaries (pythainlp `newmm`
   dictionary tokenizer). Paste the output directly -- ZWSP survives
   copy-paste and gives the destination editor real break points. Verify
   losslessness with `strip_zwsp(fixed) == original` before trusting output
   on anything consequence-bearing (see `tests/test_thai_linebreak.py`).

2. Generating a document from a template:
   ```
   python3 <repo>/scripts/generate_doc.py <template.txt.j2> <data.yaml> -o out.docx -f docx
   ```
   See `<repo>/README.md` for the template format (`#SECTION#` markers +
   Jinja2 placeholders) and the full option list (`-f txt|html|docx`).

## What this is NOT yet

Read `<repo>/README.md`'s "Status / open decisions" section before assuming
capability that isn't built: no direct Google Docs API integration yet (the
`txt` output is copy-paste-ready instead, which needs no OAuth/credentials),
no PDF output yet, only one example template exists. Do not claim these are
supported without first building and testing them.

## Design note (readout-first)

The line-break fix is a wrapper around an existing, external dictionary
tokenizer (PyThaiNLP `newmm`) -- it is not a from-scratch Thai word-
segmentation algorithm, and its accuracy is bounded by that tokenizer's own
dictionary coverage (proper nouns, neologisms, and domain jargon outside the
dictionary may tokenize imperfectly). Treat "this word boundary is correct"
as a `finite_diagnostic` readout of the tokenizer on the given input, not a
guaranteed-correct segmentation -- verify on your own template's actual
vocabulary before trusting it on a high-stakes document (a legal contract,
an official certificate).
