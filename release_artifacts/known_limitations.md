# Known limitations — v0.1.0

This release is intentionally a **local, deterministic** toolkit. The following
limitations are by design or out of scope for v0.1.0.

## Scope

- **Local-only.** No server, web API, authentication, or multi-user isolation.
- **No external intelligence.** No LLMs, embeddings, or external model APIs; no
  network calls of any kind.
- **Plaintext storage.** Store files are not encrypted by the toolkit; protect
  them with filesystem permissions.

## Extraction

- Rule-based and cue-driven. Extraction keys off patterns like "we decided",
  "I will", "TODO:", "Risk:", and question marks. Free-form phrasing without
  these cues may not be captured.
- Ownership is inferred from the speaker of an "I will" statement; commitments
  made on behalf of others are attributed to the speaker.

## Recall

- Lexical only. Search matches tokens and exact phrases; there is no semantic
  search, synonym expansion, or fuzzy matching.

## Analytics & reports

- Time-relative metrics (overdue, recent) depend entirely on the `--now` value
  you supply. This keeps results deterministic but requires you to pass the
  intended reference time.
- Risks and decisions are recorded as stated; they are not scored or ranked by
  likelihood or impact.

## Inputs

- Supported inputs are plain-text and Markdown transcripts. Other formats are out
  of scope for this release.

See [docs/production_readiness.md](../docs/production_readiness.md) and
[docs/security.md](../docs/security.md) for the full posture.
