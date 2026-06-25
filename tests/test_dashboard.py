"""Tests for analytics dashboard models."""

from organizational_memory.analytics.dashboard import (
    AnalyticsCard,
    AnalyticsDashboard,
    AnalyticsSection,
    DashboardSnapshot,
)
from organizational_memory.utils.time import parse_timestamp


def test_card_to_dict_minimal() -> None:
    card = AnalyticsCard(title="Decisions", value=5)
    assert card.to_dict() == {"title": "Decisions", "value": 5}


def test_card_to_dict_full() -> None:
    card = AnalyticsCard(
        title="Completion", value=0.75, unit="ratio", detail="3 of 4"
    )
    assert card.to_dict() == {
        "title": "Completion",
        "value": 0.75,
        "unit": "ratio",
        "detail": "3 of 4",
    }


def test_section_and_dashboard() -> None:
    section = AnalyticsSection(
        name="Decisions",
        cards=[AnalyticsCard(title="Total", value=3)],
    )
    dashboard = AnalyticsDashboard(title="Overview", sections=[section])
    data = dashboard.to_dict()
    assert data["title"] == "Overview"
    assert data["sections"][0]["name"] == "Decisions"
    assert data["sections"][0]["cards"][0]["value"] == 3


def test_snapshot_serialization() -> None:
    dashboard = AnalyticsDashboard(title="Overview", sections=[])
    snapshot = DashboardSnapshot(
        dashboard=dashboard,
        generated_at=parse_timestamp("2026-01-05T10:00:00Z"),
    )
    data = snapshot.to_dict()
    assert data["generated_at"] == "2026-01-05T10:00:00Z"
    assert data["dashboard"]["title"] == "Overview"


def test_snapshot_is_json_safe() -> None:
    import json

    dashboard = AnalyticsDashboard(
        title="Overview",
        sections=[
            AnalyticsSection(
                name="Health",
                cards=[AnalyticsCard(title="Score", value=92.5, unit="points")],
            )
        ],
    )
    snapshot = DashboardSnapshot(
        dashboard=dashboard,
        generated_at=parse_timestamp("2026-01-05T10:00:00Z"),
    )
    encoded = json.dumps(snapshot.to_dict())
    assert "Score" in encoded
