"""Deterministic workflow intelligence and analytics.

This package analyzes persisted organizational memory and produces deterministic
metrics about decisions, commitments, open loops, tasks, ownership, meetings, and
overall memory health. It uses no LLMs, embeddings, external APIs, or network
calls.
"""

from organizational_memory.analytics.decision_velocity import (
    DecisionVelocityReport,
    decision_velocity,
)

__all__ = [
    "DecisionVelocityReport",
    "decision_velocity",
]
