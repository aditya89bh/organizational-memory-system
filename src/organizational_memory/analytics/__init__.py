"""Deterministic workflow intelligence and analytics.

This package analyzes persisted organizational memory and produces deterministic
metrics about decisions, commitments, open loops, tasks, ownership, meetings, and
overall memory health. It uses no LLMs, embeddings, external APIs, or network
calls.
"""

from organizational_memory.analytics.accountability import (
    AccountabilityReport,
    OwnerAccountability,
    accountability,
)
from organizational_memory.analytics.bottlenecks import (
    BottleneckReport,
    LowSignalMeeting,
    bottlenecks,
)
from organizational_memory.analytics.commitment_completion import (
    CommitmentCompletionReport,
    commitment_completion,
)
from organizational_memory.analytics.dashboard import (
    AnalyticsCard,
    AnalyticsDashboard,
    AnalyticsSection,
    DashboardSnapshot,
)
from organizational_memory.analytics.decision_velocity import (
    DecisionVelocityReport,
    decision_velocity,
)
from organizational_memory.analytics.dependency_analytics import (
    DependencyReport,
    dependency_analytics,
)
from organizational_memory.analytics.meeting_effectiveness import (
    MeetingEffectiveness,
    MeetingEffectivenessReport,
    meeting_effectiveness,
)
from organizational_memory.analytics.memory_health import (
    HealthComponent,
    MemoryHealthReport,
    memory_health,
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
from organizational_memory.analytics.productivity import (
    ProductivityReport,
    productivity,
)
from organizational_memory.analytics.repeated_discussions import (
    RepeatedCluster,
    RepeatedDiscussionReport,
    repeated_discussions,
)
from organizational_memory.analytics.timeline_analytics import (
    TimelineAnalytics,
    timeline_analytics,
)
from organizational_memory.analytics.trends import (
    TrendPoint,
    TrendReport,
    trends,
)

__all__ = [
    "AccountabilityReport",
    "AnalyticsCard",
    "AnalyticsDashboard",
    "AnalyticsSection",
    "BottleneckReport",
    "CommitmentCompletionReport",
    "DashboardSnapshot",
    "DecisionVelocityReport",
    "DependencyReport",
    "HealthComponent",
    "LowSignalMeeting",
    "MeetingEffectiveness",
    "MeetingEffectivenessReport",
    "MemoryHealthReport",
    "OpenLoopAge",
    "OpenLoopReport",
    "OverdueItem",
    "OverdueReport",
    "OwnerAccountability",
    "OwnershipReport",
    "ProductivityReport",
    "RepeatedCluster",
    "RepeatedDiscussionReport",
    "TimelineAnalytics",
    "TrendPoint",
    "TrendReport",
    "accountability",
    "bottlenecks",
    "commitment_completion",
    "decision_velocity",
    "dependency_analytics",
    "meeting_effectiveness",
    "memory_health",
    "open_loop_metrics",
    "overdue_tasks",
    "ownership_metrics",
    "productivity",
    "repeated_discussions",
    "timeline_analytics",
    "trends",
]
