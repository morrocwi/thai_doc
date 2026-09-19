// Structured formal-letter components for Thai private-to-government and formal letters.
// This module intentionally does NOT include a Garuda/government-origin emblem.

#import "thai-worldclass.typ": thnum

#let field-row(label, value, label-width: 2.8cm, strong-label: true) = {
  grid(
    columns: (label-width, 1fr),
    column-gutter: 0.25cm,
    if strong-label { strong(label) } else { label },
    value,
  )
}

#let attachment-rows(items, label-width: 2.8cm) = {
  if items.len() > 0 {
    grid(
      columns: (label-width, 1fr),
      column-gutter: 0.25cm,
      [สิ่งที่ส่งมาด้วย],
      {
        for i in range(items.len()) [
          #thnum(i + 1). #items.at(i)
          #if i + 1 < items.len() [#linebreak()]
        ]
      },
    )
  }
}

#let private-letter-head(
  number: none,
  date: none,
  subject: none,
  attention: none,
  refer-to: none,
  attachments: (),
) = {
  set par(first-line-indent: 0cm, justify: false, spacing: 0.25em)

  if number != none { field-row([ที่], number, strong-label: false) }
  if date != none { align(right, date) }
  if subject != none { field-row([เรื่อง], subject) }
  if attention != none { field-row([เรียน], attention) }
  if refer-to != none { field-row([อ้างถึง], refer-to, strong-label: false) }
  attachment-rows(attachments)
  parbreak()
}

#let signature-block(
  signoff: [ขอแสดงความนับถือ],
  name: none,
  position: none,
  organization: none,
) = {
  set par(first-line-indent: 0cm, justify: false)
  block(breakable: false)[
    #align(center)[
      #signoff
      #v(1.5cm)
      #if name != none [(#name)]
      #if position != none [#linebreak()#position]
      #if organization != none [#linebreak()#organization]
    ]
  ]
}

#let sender-block(body) = {
  set par(first-line-indent: 0cm, justify: false)
  block(breakable: false, body)
}
