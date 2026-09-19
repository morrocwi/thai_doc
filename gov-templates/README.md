# gov-templates/

Official government-agency document templates, one folder per agency, kept
separate from the general-purpose `docs/thai-worldclass/` composition
system. When an agency-supplied authoritative template exists for the
document being drafted, it always wins over general guidance for
everything the template itself specifies (structure, fixed wording, field
order) — general guidance still applies for things the template leaves
open (e.g. how to compose the prose that fills in a blank).

## Convention

Each agency gets `gov-templates/<AGENCY_CODE>/` with:

- `source/` — the authoritative original files, exactly as supplied, with
  only personal/staff-identifying document metadata scrubbed (never the
  visible content).
- `locks/` — machine-checkable `.lock.json` conformance specs, one per
  letter template that has been locked (see the agency's own README for
  which ones and how to extend).
- `MANIFEST.md` — file-by-file index: what each file is, its type
  (locked letter / reference form / reference table).
- `README.md` — the agency-specific conformance rule and how to run the
  gate.

## Agencies currently covered

| Code | Agency | Folder |
|------|--------|--------|
| NIA | สำนักงานนวัตกรรมแห่งชาติ (National Innovation Agency, Thailand) | `NIA/` |

Adding another agency: create `gov-templates/<CODE>/` following the same
convention above. Use `scripts/gov_template_lock.py extract` to build locks
for any letter-style `.docx` templates.
