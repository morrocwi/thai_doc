# NIA (สำนักงานนวัตกรรมแห่งชาติ / National Innovation Agency, Thailand) — Social Innovation grant document set

Source: `Social_Innovation_Format-20260919T060800Z-1-001.zip`, supplied by the
founder 2026-09-19. All files below are **blank official templates** — every
copy was checked paragraph-by-paragraph before being added here and contains
no filled-in applicant data (see "Privacy scrub" below).

| # | File | Type | Purpose |
|---|------|------|---------|
| 1.1 | `1.1_องค์ประกอบเอกสาร.xlsx` | reference (xlsx) | checklist of which documents make up a complete submission |
| 1.2 | `1.2_รายละเอียดเอกสารประกอบการเบิกเงิน.pdf` | reference (pdf) | detailed requirements for disbursement-supporting documents |
| 2.1 | `2.1_จดหมายขอเบิกเงินทุนอุดหนุน (Social).docx` | **locked letter** | request to disburse grant funding for a period |
| 2.2 | `2.2_แบบรายงานความก้าวหน้าประกอบการเบิกจ่าย (Social).doc` | reference form (legacy .doc) | progress-report form accompanying a disbursement request |
| 2.3 | `2.3_ตารางคำนวนการเบิกจ่าย.xlsx` | reference (xlsx) | disbursement calculation table |
| 2.4 | `2.4_จดหมายนำส่งเอกสารเบิกเงินเพิ่มเติม (Social).docx` | **locked letter** | cover letter submitting additional disbursement documents |
| 2.5 | `2.5_ใบสำคัญรับเงิน.docx` | **locked letter** | receipt voucher (ใบสำคัญรับเงิน) |
| 3.1 | `3.1_จดหมายขอส่งรายงานรายไตรมาส (Social).docx` | **locked letter** | quarterly progress report cover letter |
| 3.2 | `3.2_แบบรายงานความก้าวหน้ารายไตรมาส (Social).doc` | reference form (legacy .doc) | quarterly progress report form |
| 4.1 | `4.1_จดหมายปิดโครงการนวัตกรรม (Social).docx` | **locked letter** | project closure letter |
| 4.2 | `4.2_แบบรายงานสรุปโครงการนวัตกรรม (Social).doc` | reference form (legacy .doc) | project summary report form |
| 5.1 | `5.1_จดหมายขอเลื่อนเบิกเงินงวด (Social).docx` | **locked letter** | request to postpone a disbursement installment |
| 6.1 | `6.1_จดหมายขอขยายระยะเวลาการดำเนินโครงการ (Social).docx` | **locked letter** | request to extend the project timeline |
| 7.1 | `7.1_จดหมายขอยกเลิกโครงการ (Social).docx` | **locked letter** | request to cancel/withdraw the project |
| 8.1 | `8.1_จดหมายขอเปลี่ยนที่อยู่ (Social).docx` | **locked letter** | notify a change of grantee address |
| 9.1 | `9.1_จดหมายขอเปลี่ยนชื่อผู้รับทุน (Social).docx` | **locked letter** | notify a change of grantee name |

**"locked letter"** = a machine-checkable `.lock.json` spec exists under
`locks/` for this file (see "100% conformance gate" below). The three
`.doc` report forms and the `.xlsx`/`.pdf` reference files are not yet
locked (open item — they are structured forms/tables, not free-form
letters, and need a different extraction approach than the dot-leader
paragraph tokenizer used for the letters; see README "Not yet built").

## Privacy scrub (done before these files were added here)

The original zip's `.docx`/`.xlsx` files carried real NIA/BIDF staff names
in Office document properties (`dc:creator`, `cp:lastModifiedBy`: four
distinct individual names across the set), the `.pdf` carried a real author
name in its metadata, and the three `.doc` legacy files carried a real
staff name in their OLE property stream (`last_saved_by`) plus an org unit
tag (`author: BIDF`, `company: NSTDA`). Names are intentionally not
reproduced here — republishing the individuals' names in this public,
permanently-indexed file would reintroduce the exact PII the scrub below
was meant to remove, just relocated from binary metadata into searchable
Markdown/git history. None of this appeared in the visible document text (every visible field is a blank dot-leader placeholder — verified by
reading every paragraph of every file before scrubbing). All of it was
stripped from the copies in `source/` before they were committed:
`docx`/`xlsx` via rewriting `docProps/core.xml` in place, the `pdf` via
`pikepdf` metadata clearing, the three `.doc` files via a LibreOffice UNO
script that clears `DocumentProperties.Author`/`ModifiedBy` and re-saves in
the same legacy format — content verified byte-identical (converted both
original and scrubbed copies to `.txt` and diffed: identical) before and
after, only the personal metadata changed.
