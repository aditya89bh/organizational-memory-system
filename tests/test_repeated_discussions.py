"""Tests for the repeated discussion detector."""

from pathlib import Path

from organizational_memory.analytics.repeated_discussions import (
    repeated_discussions,
)
from organizational_memory.models import DiscussionTopic, OpenLoop
from organizational_memory.storage.json_store import JSONStore


def _store(tmp_path: Path) -> JSONStore:
    store = JSONStore(tmp_path / "memory.json")
    store.save_record(
        DiscussionTopic(id="dt1", title="Pricing strategy", source_meeting_id="m1")
    )
    store.save_record(
        DiscussionTopic(id="dt2", title="pricing  strategy!", source_meeting_id="m2")
    )
    store.save_record(
        DiscussionTopic(id="dt3", title="Hiring plan", source_meeting_id="m1")
    )
    store.save_record(
        OpenLoop(id="o1", question="How do we handle auth?", source_meeting_id="m1")
    )
    store.save_record(
        OpenLoop(id="o2", question="how do we handle auth", source_meeting_id="m3")
    )
    return store


def test_repeated_topic_cluster(tmp_path: Path) -> None:
    report = repeated_discussions(_store(tmp_path))
    assert len(report.topic_clusters) == 1
    cluster = report.topic_clusters[0]
    assert cluster.key == "pricing strategy"
    assert cluster.occurrences == 2
    assert cluster.record_ids == ("dt1", "dt2")
    assert cluster.meeting_ids == ("m1", "m2")


def test_repeated_open_loop_cluster(tmp_path: Path) -> None:
    report = repeated_discussions(_store(tmp_path))
    assert len(report.open_loop_clusters) == 1
    cluster = report.open_loop_clusters[0]
    assert cluster.occurrences == 2
    assert cluster.record_ids == ("o1", "o2")
    assert cluster.meeting_ids == ("m1", "m3")


def test_repeated_keywords(tmp_path: Path) -> None:
    report = repeated_discussions(_store(tmp_path))
    assert report.repeated_keywords.get("pricing") == 2
    assert report.repeated_keywords.get("strategy") == 2
    assert "hiring" not in report.repeated_keywords


def test_no_repeats(tmp_path: Path) -> None:
    store = JSONStore(tmp_path / "single.json")
    store.save_record(DiscussionTopic(id="dt1", title="Unique topic"))
    report = repeated_discussions(store)
    assert report.topic_clusters == []
    assert report.repeated_keywords == {}
