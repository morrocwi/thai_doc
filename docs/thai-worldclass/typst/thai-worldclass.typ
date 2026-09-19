// Thai World-Class Publication System — Typst compositor v2.1
// Verified design target: Typst >= 0.15.1
// Renderer-neutral input only: do not feed Google Docs U+2009 adaptations here.

#let thnum(value) = str(value)
  .replace("0", "๐")
  .replace("1", "๑")
  .replace("2", "๒")
  .replace("3", "๓")
  .replace("4", "๔")
  .replace("5", "๕")
  .replace("6", "๖")
  .replace("7", "๗")
  .replace("8", "๘")
  .replace("9", "๙")

#let thai-worldclass(
  body,
  font: ("Sarabun", "TH Sarabun New", "Noto Sans Thai"),
  size: 16pt,
  margin: (top: 2.5cm, right: 2cm, bottom: 2cm, left: 3cm),
  justify: true,
  first-indent: 2.5cm,
  all-indents: true,
) = {
  set page("a4", margin: margin)
  set text(
    font: font,
    size: size,
    lang: "th",
    region: "TH",
  )
  set par(
    justify: justify,
    linebreaks: "optimized",
    first-line-indent: (amount: first-indent, all: all-indents),
    leading: 0.65em,
    spacing: 0.65em,
    justification-limits: (
      // Conservative v2.1 policy: constrain word-space variation.
      // Typst may exceed max if no feasible justification exists, so PDF QA remains mandatory.
      spacing: (min: 90%, max: 120%),
      // Do not character-track Thai by default; combining-cluster appearance is font-sensitive.
      tracking: (min: 0em, max: 0em),
    ),
  )
  body
}
