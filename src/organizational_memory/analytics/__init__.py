"""Deterministic workflow intelligence and analytics.

This package analyzes persisted organizational memory and produces deterministic
metrics about decisions, commitments, open loops, tasks, ownership, meetings, and
overall memory health. It uses no LLMs, embeddings, external APIs, or network
calls.
"""

from organizational_memory.analytics.commitment_completion import (
    CommitmentCompletionReport,
    commitment_completion,
)
from organizational_memory.analytics.decision_velocity import (
    DecisionVelocityReport,
    decision_velocity,
)
from organizational_memory.analytics.open_loop_metrics import (
    OpenLoopAge,
    OpenLoopReport,
    open_loop_metrics,
)
from organizational_memory.analytics.overdue_tasks import (
    OverdueItem,
    OverdueReport,
    overdue_tasks,
)
from organizational_memory.analytics.ownership_metrics import (
    OwnershipReport,
    ownership_metrics,
)

__all__ = [
    "CommitmentCompletionReport",
    "DecisionVelocityReport",
    "OpenLoopAge",
    "OpenLoopReport",
    "OverdueItem",
    "OverdueReport",
    "OwnershipReport",
    "commitment_completion",
    "decision_velocity",
    "open_loop_metrics",
    "overdue_tasks",
    "ownership_metrics",
]
