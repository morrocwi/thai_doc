# Center for AI Civic Knowledge — Canonical Thai Preprint Template

แม่แบบ LaTeX กลางสำหรับ paper ภาษาไทยของ **Center for AI Civic Knowledge**

## กฎแบรนด์

ใช้ `aick-thai-preprint.cls` เป็น class หลักเท่านั้นสำหรับ preprint ภาษาไทยของศูนย์ฯ ที่ใช้ house style นี้ อย่าแก้ตำแหน่งโลโก้, PREPRINT, front matter, page 2 methodology note, running header/footer หรือ palette ในไฟล์ `.tex` รายบทความ หากต้องแก้ระบบภาพรวม ให้แก้ class กลางและเพิ่ม version ของ template แทน

## โครงสร้างบังคับ

1. หน้า 1 — PREPRINT, version/date, โลโก้เต็มแบบ overlay มุมขวาบน, ชื่อเรื่องและข้อมูลผู้เขียนชิดซ้าย, ORCID, บทคัดย่อ, เว้นหนึ่งบรรทัด, คำสำคัญ
2. หน้า 2 — `สถานะบทความและวิถีวิทยาการสร้างความรู้` เป็นหน้าของตัวเอง
3. หน้า 3 — บทนำขึ้นหน้าใหม่
4. เนื้อหาหลัก — A4, one-column, global academic preprint profile
5. ท้ายเล่ม — กิตติกรรมประกาศ, คำประกาศของผู้เขียน, เอกสารอ้างอิง

## การใช้งาน

เก็บไฟล์ต่อไปนี้ไว้ในโฟลเดอร์เดียวกัน:

- `aick-thai-preprint.cls`
- `aick-paper-template.tex`
- `ai-civic-knowledge-full-logo.png`

คอมไพล์ด้วย XeLaTeX:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error aick-paper-template.tex
```

## สิ่งที่แก้ได้ใน manuscript

แก้เฉพาะ metadata ผ่าน `\AICK...` commands และเนื้อหาหลัง `\begin{document}` เช่น title, subtitle, author, ORCID, version, date, abstract, keywords และบทต่าง ๆ

บทคัดย่อแนะนำประมาณ 1,400–1,700 ตัวอักษรไทย และควรทำให้เห็นในครั้งเดียว: **ปัญหา → ข้อเสนอ/นิยาม → กลไก → ข้อสรุปหลัก**

## สถานะ

House template v1.0 — 20 September 2026.
