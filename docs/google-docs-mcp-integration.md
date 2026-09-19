# External integration: google-docs-mcp

`scripts/google_docs_batch.py` in this repo builds Google Docs API
`batchUpdate` requests but deliberately never shipped a live-apply path
with real credentials (see that script's module docstring and
`scripts/README_google_docs_batch.md`) — bring-your-own-credentials, no
network call without them, `apply_live()` untested against a real Google
Doc in this environment.

For anyone who wants a real, live Google Docs connection (read/write an
actual document, not just generate request JSON), the recommended external
tool is:

**https://github.com/a-bonus/google-docs-mcp** (`@a-bonus/google-docs-mcp`
on npm) — an MCP server for Claude Desktop/Cursor/Windsurf/any MCP client,
covering Google Docs, Sheets, Drive, Gmail, Calendar, and Apps Script.

## Vetting note (2026-09-19)

Evaluated per this workspace's external-tool vetting discipline before
recommending it here (`~/.claude/skill-library/VETTING_PROTOCOL.md`
red-flag scan, adapted for an MCP server rather than a Claude Skill, since
an MCP server gets live tool-calling access to a real account — a higher
blast radius than a passive skill file, so it earned the same scrutiny):

- **License**: MIT. **Maintenance**: 662 stars, 216 forks, pushed
  2026-08-31, not archived — active.
- **Dependencies**: `googleapis`, `google-auth-library`,
  `@google-cloud/firestore` (official Google packages), `fastmcp`,
  `markdown-it`, `zod` — all well-known, legitimate packages. No unknown
  or suspicious dependencies.
- **Red-flag scan of the full source tree** (cloned and grepped, not just
  the README): no `eval`/`new Function`/`child_process`/`execSync`, no
  outbound network calls to any domain other than Google's own API/OAuth
  endpoints (`googleapis.com`, `accounts.google.com`,
  `oauth2.googleapis.com`, `script.google.com`) plus `localhost` (the
  OAuth redirect) — no exfiltration path to a third party. No
  prompt-injection-style phrasing ("ignore previous instructions" etc.)
  found anywhere. No base64/obfuscated blobs.
- **Credential handling**: bring-your-own Google Cloud OAuth client
  (`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` env vars, the installer
  creates their own in Google Cloud Console) — matches this repo's own
  bring-your-own-credentials model exactly. The refresh token is written
  to `~/.config/google-docs-mcp/token.json` with file mode `0600`
  (owner-read/write only) — reasonable local-secret hygiene. Standard
  localhost-redirect OAuth desktop flow, not a third-party-hosted auth
  broker (a self-hosted remote-deployment option exists too, opt-in, not
  the default).
- **Scope is much broader than this repo needs.** The full tool covers
  Gmail (read/send/delete/draft), Calendar (create/update/delete events),
  Apps Script (create and run script projects bound to a Doc/Sheet — this
  is real code-execution capability under the installer's Google
  identity), Sheets, and Drive, in addition to Docs. **thai_doc only needs
  the Docs (and optionally Drive, for listing/creating files) surface.**
  Because Google OAuth scopes are granted per-API at the installer's own
  Google Cloud Console project, an installer who only wants thai_doc's use
  case can enable just the Docs API (and Drive if wanted) in their own
  project and skip enabling Gmail/Calendar/Apps Script — the tool's own
  README setup steps list enabling each API as a separate step, so this is
  a real, available choice, not an all-or-nothing grant. **Recommendation:
  do this** — enable only what you intend to use.

Not independently code-reviewed line-by-line (161 non-test TypeScript
source files — out of scope for what this integration note needs); the
scan above covers the standard red-flag categories, dependency
legitimacy, and the credential/network surface, which is what matters for
a "should we point installers at this" decision. Re-vet if this repo's own
upstream changes substantially before relying on a newer claim about it.

## How it relates to this repo's own tools

- `scripts/generate_doc.py` / `scripts/google_docs_batch.py` compose Thai
  content and (for the batch script) produce raw `batchUpdate` request
  JSON — useful as a dry-run/audit artifact, or as an input to a custom
  live-apply script using your own Google credentials directly.
- `google-docs-mcp` is a separate, more full-featured path: connect it to
  an AI session and have the AI call its higher-level tools
  (`insertText`, `applyParagraphStyle`, `findAndReplace`,
  `insertTableWithData`, etc.) directly against a real document. It does
  **not** currently consume this repo's `google_docs_batch.py` JSON output
  directly — the two are complementary, not wired together. Building a
  small adapter (translate our `insertText`/`updateParagraphStyle`
  batchUpdate requests into a sequence of calls to this MCP's tools) is
  possible future work, not done here.
- For a `gov-templates/*/locks/*.lock.json` detailed sub-template, the
  fail-closed conformance check in `scripts/gov_template_lock.py` still
  applies regardless of which delivery path (this repo's own script, or
  `google-docs-mcp`) is used to actually write the filled-in letter — run
  it on the final text before treating a draft as done, per
  `gov-templates/<AGENCY>/README.md`.

## Setup (summary — see the tool's own README for full detail)

```bash
# 1. Create your own OAuth client in Google Cloud Console, enable ONLY
#    the APIs you need (Docs, +Drive if you want file listing/creation).
# 2. Authorize once:
GOOGLE_CLIENT_ID="..." GOOGLE_CLIENT_SECRET="..." \
  npx -y @a-bonus/google-docs-mcp auth

# 3. Add to your MCP client config (Claude Desktop / Claude Code / etc.):
```
```json
{
  "mcpServers": {
    "google-docs": {
      "command": "npx",
      "args": ["-y", "@a-bonus/google-docs-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

This repo ships none of the above — no client ID, no secret, no token.
Bring your own, same as every other live-service integration point in
this repo.
