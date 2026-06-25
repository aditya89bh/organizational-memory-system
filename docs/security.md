# Security

This document describes the security posture of the organizational-memory
toolkit. It is intentionally honest and scoped: the project is a local,
deterministic library and command-line tool, not a hosted service.

## Local-only operation

The toolkit runs entirely on the machine that invokes it. There is no server
component, no background daemon, and no inter-process communication beyond
reading and writing the local store files you specify.

## No network calls

No part of the toolkit opens a network connection. There is:

- no telemetry or usage reporting,
- no automatic update or download mechanism,
- no remote logging or error-reporting service.

Error reporting (`organizational_memory.observability.error_reporting`) builds
report objects **in process**; it never transmits them anywhere.

## No external APIs, models, or embeddings

Extraction, recall, analytics, and reporting are rule-based and deterministic.
The toolkit does not call language models, embedding services, or any third-party
API. The same input always produces the same output.

## No secret management

The toolkit does not read, store, request, or manage secrets such as passwords,
API keys, or tokens. It has no credential store and no authentication layer. If
you place sensitive content into a transcript, that content is treated as
ordinary text.

## Supported input assumptions

- Transcripts are plain UTF-8 text supplied by a trusted operator.
- Store files (JSON or SQLite) are created and owned by the operator.
- The toolkit assumes inputs are not adversarial. It validates structure and
  rejects malformed configuration, but it is not a sandbox for untrusted input.

## Data privacy limitations

- All extracted records are written to the local store file in plain text.
- Store files are **not encrypted at rest**. Protect them with filesystem
  permissions and disk encryption as appropriate for your environment.
- Reports and exports (Markdown, JSON, CSV) contain the same content as the
  store and should be handled with the same care.

## Known risks

- **Plaintext storage.** Anyone with read access to a store file can read its
  contents.
- **Untrusted transcripts.** Feeding very large or pathological inputs can
  consume CPU and memory; there are no built-in resource quotas.
- **Path handling.** Store and output paths are taken from the operator. Point
  them only at locations you intend to write to.
- **No multi-user isolation.** The toolkit has no concept of users, roles, or
  access control.

## Responsible disclosure

Please report suspected vulnerabilities privately. See
[SECURITY.md](../SECURITY.md) for the reporting process and supported versions.
