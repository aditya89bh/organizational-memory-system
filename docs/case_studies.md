# Case studies

These case studies are **deterministic**: each uses a fixed transcript bundled
with the toolkit, so the extracted memory and outputs are reproducible. They show
the same pipeline applied to different meeting types. Every case ends with an
honest limitation note.

Reproduce any case study with the demo command, for example:

```bash
organizational-memory demo startup
```

## 1. Startup product meeting

**Input** (`demos/startup.py`):

```
[09:00] Aditya: We decided to delay the launch to next month.
[09:02] Priya: I will finalize the pricing page.
[09:04] Rahul: The launch is blocked by the security review.
[09:05] Aditya: What is our runway?
Risk: we might run out of cash before the next round.
TODO: prepare the investor update.
Topic: Launch delay
```

**Extracted memory:**

- Decision: "We decided to delay the launch to next month."
- Commitment: "I will finalize the pricing page."
- Task: "TODO: prepare the investor update."
- Open loop: "What is our runway?"
- Risk: "Risk: we might run out of cash before the next round."
- Action items: 2

**Recall / analytics / report:** recalling `"launch"` surfaces the launch-delay
decision; a follow-up report lists the open commitment and the unresolved runway
question.

**Limitation:** extraction is rule-based and keys off cues like "we decided",
"I will", "TODO:", "Risk:", and question marks. Free-form phrasing without these
cues may not be captured.

## 2. Sprint planning review

**Input** (`demos/sprint.py`):

```
[10:00] Maria: We decided to adopt the new CI pipeline.
[10:02] Sam: I will own the migration to the new runners.
[10:03] Dana: I will write the regression tests.
[10:05] Maria: The rollout is blocked by the staging outage.
[10:06] Sam: Who signs off on the release?
TODO: update the deployment runbook.
Topic: Sprint scope
```

**Extracted memory:**

- Decision: "We decided to adopt the new CI pipeline."
- Commitments: "I will own the migration to the new runners.",
  "I will write the regression tests."
- Task: "TODO: update the deployment runbook."
- Open loop: "Who signs off on the release?"
- Action items: 3

**Recall / analytics / report:** a weekly report groups the two commitments by
owner; analytics shows owner load split across Sam and Dana.

**Limitation:** ownership is inferred from the speaker of an "I will" statement.
Commitments made on behalf of others are attributed to the speaker.

## 3. Board review

**Input** (`demos/board.py`):

```
[14:00] Aditya: We decided to expand into the European market.
[14:03] Lena: We decided to hire a new head of sales.
[14:05] Marcus: The expansion is blocked by regulatory approval.
[14:07] Aditya: What is our compliance timeline?
Risk: currency exposure could reduce margins.
Risk: hiring delays may slow the expansion.
Topic: Market expansion
```

**Extracted memory:**

- Decisions: "We decided to expand into the European market.",
  "We decided to hire a new head of sales."
- Open loop: "What is our compliance timeline?"
- Risks: "Risk: currency exposure could reduce margins.",
  "Risk: hiring delays may slow the expansion."

**Recall / analytics / report:** a decision report lists both strategic
decisions; an organizational-memory report highlights the two open risks.

**Limitation:** the toolkit records risks as stated; it does not score or rank
their likelihood or impact.

## 4. Company memory recall

**Input:** all three meetings above are ingested into a single store (41 records
total across decisions, commitments, tasks, open loops, risks, action items,
participants, and topics).

**Recall examples:**

```
recall "launch"   -> 3 hits
recall "pricing"  -> 2 hits
```

**Report:** an organizational-memory report over the combined store renders 7
deterministic sections spanning decisions, commitments, open loops, and risks.

**Limitation:** recall is lexical. It matches tokens and exact phrases; it does
not perform semantic search, synonym expansion, or fuzzy matching.

## 5. Weekly operating review

**Input:** the combined company memory, queried at a fixed reference time
(`--now 2026-03-01T00:00:00Z`).

**Output:** a weekly report assembles outstanding commitments, open loops, and
recent decisions into a single digest. Because the reference time is explicit,
the "overdue" and "recent" determinations are reproducible.

```bash
organizational-memory report weekly --store memory.json --now 2026-03-01T00:00:00Z
```

**Limitation:** time-relative metrics depend entirely on the `--now` value you
provide. There is no wall-clock dependency, which keeps results deterministic but
means you must pass the intended reference time.
