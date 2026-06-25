# Security Policy

## Supported Versions

The project is in early development. Security fixes are applied to the latest
released version on the `main` branch.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately rather than
opening a public issue.

- Email: aditya89bh@gmail.com
- Include a clear description, reproduction steps, and the affected version.

You can expect an acknowledgement within a few business days. Once the issue is
confirmed, we will work on a fix and coordinate a disclosure timeline with you.

## Security model at a glance

This is a **local, deterministic** organizational-memory toolkit. It is designed
to run on a single machine against local files.

- **No network calls.** The toolkit does not contact any remote service, send
  telemetry, or download anything at runtime.
- **No external APIs, models, or embeddings.** All extraction, recall,
  analytics, and reporting are rule-based and run in-process.
- **No secret management.** The toolkit does not store, request, or manage
  credentials, tokens, or API keys.
- **Local data only.** Records are persisted to local JSON or SQLite files that
  you control.

For the full threat model, data-handling notes, and known risks, see
[docs/security.md](docs/security.md).
