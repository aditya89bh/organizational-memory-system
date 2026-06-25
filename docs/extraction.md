# Extraction

Phase 3 adds a **deterministic, rule-based extraction layer**. It turns raw
meeting transcripts and markdown notes into structured organizational memory
records using fixed heuristics and pattern matching.

> [!IMPORTANT]
> Extraction is fully deterministic. It uses no LLMs, no external APIs, and no
> network calls. The same input always produces the same output.

## Architecture

Extraction is a pipeline of small, single-responsibility modules:

1. **Ingestion** (`organizational_memory.ingestion`) loads input into a
   `Transcript` from a string or file, for both plain text and markdown.
2. **Normalization** (`extraction.normalization`) cleans whitespace, bullets,
   leading timestamps, blank-line runs, and common unicode characters.
3. **Speaker parsing** (`extraction.speakers`) detects speaker turns such as
   `Aditya: ...`, `Priya - ...`, and `[10:30] Rahul: ...`.
4. **Segmentation** (`extraction.segmentation`) classifies each non-blank line
   into a typed `Segment` (`heading`, `speaker_turn`, `bullet`, `paragraph`).
5. **Extractors** scan the segments and emit Phase 2 domain records.
6. **Pipeline** (`extraction.pipeline`) runs the whole flow and returns a typed
   `ExtractionResult`, then applies confidence scoring, audit traces, and the
   active configuration.

## Supported input formats

- **Plain text** transcripts (`load_transcript_from_string`,
  `load_transcript_from_file`).
- **Markdown** notes (`load_markdown_from_string`, `load_markdown_from_file`),
  where headings and bullet lines are preserved.

## Extractors

Each extractor matches a fixed set of case-insensitive marker phrases and
produces records using the Phase 2 models:

| Extractor             | Output record    | Example markers                                  |
| --------------------- | ---------------- | ------------------------------------------------ |
| `decision_extractor`  | `Decision`       | `we decided`, `decision:`, `approved`            |
| `commitment_extractor`| `Commitment`     | `I will`, `I'll`, `I commit to`, `we will`       |
| `task_extractor`      | `Task`           | `todo:`, `task:`, `action:`, `[ ]`, `needs to`   |
| `question_extractor`  | `OpenLoop`       | trailing `?`, `open question:`, `unresolved:`    |
| `dependency_extractor`| `Dependency`     | `blocked by`, `depends on`, `waiting for`        |
| `risk_extractor`      | `Risk`           | `risk:`, `concern:`, `might fail`, `could delay` |
| `action_item_extractor`| `ActionItem`    | task-like bullets and speaker commitments        |
| `participant_extractor`| `Participant`   | attendee lines and speaker turns                 |
| `topic_extractor`     | `DiscussionTopic`| markdown headings, `topic:` lines                |

`entities` additionally surfaces conservative person, date, and capitalized
topic phrases.

## Confidence scoring

`extraction.confidence` assigns each record a deterministic score in `[0, 1]`
based on:

- **Marker strength** — explicit markers ending in `:` score highest, decisive
  phrases next, structural matches and bare questions lower.
- **Owner detected** — a known owner adds a small bonus.
- **Due date detected** — a parsed due date adds a small bonus.
- **Source line quality** — very short or very long lines are penalized.
- **Ambiguous phrasing** — hedging words such as `maybe` or `perhaps` are
  penalized.

The score is written to each record's metadata under the `confidence` key.

## Audit traces

`extraction.audit` exposes an `ExtractionTrace` for every extracted record,
linking it back to its source:

- `record_id`
- `extractor`
- `matched_phrase`
- `source_line`
- `segment_id`
- `confidence`

Traces are collected on `ExtractionResult.traces`.

## Configuration

`ExtractionConfig` controls pipeline behavior deterministically:

- `min_confidence` — drop records below a threshold.
- `enabled_extractors` — run only a subset of extractors.
- `parse_dates` — toggle date entity extraction.
- `filter_duplicates` — drop duplicate records per category.
- `strict` — raise when no records are extracted at all.

## Known limitations

- Extraction is heuristic and pattern-based; it does not understand semantics.
- Owners are taken from speaker attribution; un-attributed commitments and tasks
  use the placeholder owner `unattributed`.
- Date phrases are surfaced as entities but are not converted into due dates.
- Capitalized phrase detection is conservative and may miss or over-match
  topic-like names.

## Example usage

```python
from organizational_memory.extraction import ExtractionConfig, run_extraction

transcript = """
Aditya: We decided to launch the beta on Friday.
Priya: I will prepare the onboarding docs.
Rahul: The launch is blocked by the security review.
Aditya: What is our rollback plan?
"""

result = run_extraction(transcript, ExtractionConfig(min_confidence=0.6))

for decision in result.decisions:
    print(decision.title, decision.metadata["confidence"])

for trace in result.traces:
    print(trace.extractor, trace.matched_phrase, trace.confidence)
```

Run the benchmark over the bundled samples:

```bash
python scripts/run_extraction_benchmarks.py
```
