# Domain Schemas

This document describes the Phase 2 domain models that make up the organizational
memory. All record models extend the shared `BaseRecord`, which provides an `id`
and `created_at` / `updated_at` timestamps, plus `to_dict` and `to_json` helpers.

## Core domain models

| Model | Purpose | Key fields |
| --- | --- | --- |
| `Meeting` | A meeting that memory is extracted from | `title`, `started_at`, `ended_at`, `participants`, `source` |
| `Participant` | A person involved in meetings or records | `name`, `email`, `role`, `organization` |
| `Decision` | A decision reached by the organization | `title`, `description`, `owner_id`, `rationale`, `decided_at`, `status` |
| `Commitment` | A promise to deliver something | `owner_id`, `description`, `due_at`, `status` |
| `Task` | A unit of work | `title`, `description`, `owner_id`, `due_at`, `priority`, `status` |
| `OpenLoop` | An unresolved question or pending issue | `question`, `owner_id`, `status`, `due_at` |
| `Dependency` | A directed dependency between records | `source_id`, `target_id`, `dependency_type`, `status` |
| `Risk` | An identified risk | `title`, `description`, `severity`, `likelihood`, `status` |
| `DiscussionTopic` | A topic discussed in a meeting | `title`, `summary`, `participant_ids`, `started_at`, `ended_at` |
| `ActionItem` | A lightweight extracted follow-up | `description`, `owner_id`, `due_at`, `status` |
| `MemoryEvent` | An append-only memory event | `event_type`, `entity_type`, `entity_id`, `occurred_at`, `payload` |

## Enumerations

String-valued enumerations capture lifecycle states and grades:

- `DecisionStatus`: `proposed`, `accepted`, `rejected`, `superseded`
- `CommitmentStatus`: `pending`, `in_progress`, `completed`, `cancelled`
- `TaskStatus`: `todo`, `in_progress`, `blocked`, `done`, `cancelled`
- `OpenLoopStatus`: `open`, `resolved`, `dismissed`
- `RiskStatus`: `identified`, `mitigated`, `accepted`, `closed`
- `DependencyStatus`: `pending`, `resolved`, `blocked`
- `Priority`: `low`, `medium`, `high`, `urgent`
- `Severity`: `low`, `medium`, `high`, `critical`
- `Likelihood`: `low`, `medium`, `high`

Because the enums are string-valued, they serialize directly to their string
values and reconstruct from them.

## Relationships

Relationships connect two entities through a typed reference:

- `EntityRef`: a typed reference with `entity_type` and `entity_id`.
- `EntityRelationship`: a directed `source` → `target` link with a
  `relationship_type`.
- `RelationshipType`: `decision_to_task`, `decision_to_commitment`,
  `task_blocks_task`, `risk_affects_decision`, `open_loop_blocks_decision`.

## Ownership model

Ownership is tracked with three primitives:

- `OwnerRef`: a lightweight reference to an owning participant.
- `Assignment`: assigns an entity (`entity_type` + `entity_id`) to an `owner_id`.
- `OwnershipChange`: records a transfer from `previous_owner_id` to
  `new_owner_id`.

## Audit metadata

`AuditMetadata` captures provenance independently of a record's own timestamps:
`created_at`, `updated_at`, `created_by`, `updated_by`, `source`, and `trace_id`.
The `touched()` helper returns a copy with `updated_at` advanced.

## Timeline

`TimelineEntry` is a dated entry referencing an entity, and
`OrganizationalTimeline` collects entries and returns them ordered by timestamp
via `ordered()`.

## Persistence

`organizational_memory.persistence` provides `to_dict` and `from_dict` for
converting any domain dataclass to and from JSON-compatible dictionaries.
Datetimes, enums, nested dataclasses, and optional fields are handled
automatically.

## Example JSON

A serialized `Decision`:

```json
{
  "id": "0f8e...",
  "created_at": "2026-06-24T09:00:00Z",
  "updated_at": "2026-06-24T09:00:00Z",
  "title": "Adopt CI",
  "description": "Use GitHub Actions for all checks",
  "owner_id": "alice",
  "rationale": "Reduces manual toil",
  "decided_at": "2026-06-24T09:00:00Z",
  "status": "accepted",
  "source_meeting_id": "m1",
  "metadata": {}
}
```

A serialized `EntityRelationship`:

```json
{
  "id": "a1b2...",
  "created_at": "2026-06-24T09:00:00Z",
  "updated_at": "2026-06-24T09:00:00Z",
  "source": { "entity_type": "decision", "entity_id": "d1" },
  "target": { "entity_type": "task", "entity_id": "t1" },
  "relationship_type": "decision_to_task",
  "description": null,
  "metadata": {}
}
```
