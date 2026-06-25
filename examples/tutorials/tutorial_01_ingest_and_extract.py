"""Tutorial 1: ingest a transcript and extract structured memory.

Run it with::

    python examples/tutorials/tutorial_01_ingest_and_extract.py

This tutorial shows the first step of the pipeline: turning raw meeting text into
structured records (decisions, commitments, tasks, open loops, and more) using
the deterministic, rule-based extractor. Nothing is persisted and no network is
used.
"""

from organizational_memory.extraction.pipeline import run_extraction

TRANSCRIPT = """# Product Sync

Attendees: Aditya, Priya, Rahul

[09:00] Aditya: We decided to ship the beta next week.
[09:02] Priya: I will prepare the release notes.
[09:04] Rahul: The release is blocked by the load test.
[09:05] Aditya: What is our rollback plan?
Risk: the migration could fail under peak traffic.
TODO: schedule the load test.
Topic: Beta release
"""


def main() -> int:
    result = run_extraction(TRANSCRIPT)
    print("Extracted structured memory:")
    print(f"  participants : {len(result.participants)}")
    print(f"  decisions    : {len(result.decisions)}")
    print(f"  commitments  : {len(result.commitments)}")
    print(f"  tasks        : {len(result.tasks)}")
    print(f"  open loops   : {len(result.open_loops)}")
    print(f"  risks        : {len(result.risks)}")
    print(f"  action items : {len(result.action_items)}")

    print("\nDecisions:")
    for decision in result.decisions:
        print(f"  - {decision.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
