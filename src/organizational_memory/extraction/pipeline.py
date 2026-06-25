"""End-to-end deterministic extraction pipeline."""

from dataclasses import dataclass, field
from typing import TypeVar

from organizational_memory.extraction.action_item_extractor import (
    extract_action_items,
)
from organizational_memory.extraction.audit import (
    ExtractionTrace,
    TraceableRecord,
    build_traces,
)
from organizational_memory.extraction.commitment_extractor import (
    extract_commitments,
)
from organizational_memory.extraction.confidence import (
    MetadataRecord,
    annotate_confidence,
)
from organizational_memory.extraction.config import (
    ExtractionConfig,
    default_config,
)
from organizational_memory.extraction.decision_extractor import extract_decisions
from organizational_memory.extraction.dependency_extractor import (
    extract_dependencies,
)
from organizational_memory.extraction.entities import (
    ExtractedEntities,
    extract_entities,
)
from organizational_memory.extraction.errors import (
    EmptyTranscriptError,
    UnsupportedInputError,
)
from organizational_memory.extraction.normalization import normalize_text
from organizational_memory.extraction.participant_extractor import (
    extract_participants,
)
from organizational_memory.extraction.provenance import (
    CONFIDENCE_KEY,
    SOURCE_LINE_KEY,
)
from organizational_memory.extraction.question_extractor import extract_questions
from organizational_memory.extraction.risk_extractor import extract_risks
from organizational_memory.extraction.segmentation import Segment, segment_text
from organizational_memory.extraction.speakers import (
    SpeakerTurn,
    parse_speaker_turns,
)
from organizational_memory.extraction.task_extractor import extract_tasks
from organizational_memory.extraction.topic_extractor import extract_topics
from organizational_memory.ingestion.transcript_loader import Transcript
from organizational_memory.models.action_item import ActionItem
from organizational_memory.models.commitment import Commitment
from organizational_memory.models.decision import Decision
from organizational_memory.models.dependency import Dependency
from organizational_memory.models.discussion_topic import DiscussionTopic
from organizational_memory.models.open_loop import OpenLoop
from organizational_memory.models.participant import Participant
from organizational_memory.models.risk import Risk
from organizational_memory.models.task import Task


@dataclass(frozen=True)
class ExtractionResult:
    """The structured organizational memory extracted from a transcript."""

    segments: list[Segment] = field(default_factory=list)
    speaker_turns: list[SpeakerTurn] = field(default_factory=list)
    participants: list[Participant] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    commitments: list[Commitment] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    open_loops: list[OpenLoop] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    topics: list[DiscussionTopic] = field(default_factory=list)
    entities: ExtractedEntities = field(default_factory=ExtractedEntities)
    traces: list[ExtractionTrace] = field(default_factory=list)


_RecordT = TypeVar("_RecordT", bound=MetadataRecord)
_TraceableT = TypeVar("_TraceableT", bound=TraceableRecord)

_PRIMARY_FIELDS = ("name", "title", "question", "description")


def _primary_text(record: object) -> str:
    for attr in _PRIMARY_FIELDS:
        value = getattr(record, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def _as_transcript(source: Transcript | str) -> Transcript:
    if isinstance(source, Transcript):
        return source
    if isinstance(source, str):
        return Transcript(text=source)
    raise UnsupportedInputError(
        f"unsupported extraction input type: {type(source).__name__}"
    )


def _postprocess(
    name: str,
    records: list[_RecordT],
    config: ExtractionConfig,
) -> None:
    """Apply enabled, confidence, and duplicate filtering to ``records``."""
    if not config.is_enabled(name):
        records.clear()
        return
    annotate_confidence(records)
    kept: list[_RecordT] = []
    seen: set[str] = set()
    for record in records:
        confidence = float(record.metadata.get(CONFIDENCE_KEY, "0"))
        if confidence < config.min_confidence:
            continue
        if config.filter_duplicates:
            source_line = record.metadata.get(SOURCE_LINE_KEY, "").lower()
            fingerprint = f"{source_line}||{_primary_text(record)}"
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
        kept.append(record)
    records[:] = kept


def _handle_group(
    name: str,
    records: list[_TraceableT],
    config: ExtractionConfig,
    result: "ExtractionResult",
) -> int:
    """Filter ``records`` and append their audit traces to ``result``."""
    _postprocess(name, records, config)
    result.traces.extend(build_traces(records))
    return len(records)


def run_extraction(
    source: Transcript | str,
    config: ExtractionConfig | None = None,
) -> ExtractionResult:
    """Run the full deterministic extraction pipeline over ``source``."""
    config = config or default_config()
    transcript = _as_transcript(source)
    if transcript.is_empty:
        raise EmptyTranscriptError("transcript has no extractable content")
    text = normalize_text(transcript.text)
    segments = segment_text(text)
    result = ExtractionResult(
        segments=segments,
        speaker_turns=parse_speaker_turns(text),
        participants=extract_participants(segments),
        decisions=extract_decisions(segments),
        commitments=extract_commitments(segments),
        tasks=extract_tasks(segments),
        open_loops=extract_questions(segments),
        dependencies=extract_dependencies(segments),
        risks=extract_risks(segments),
        action_items=extract_action_items(segments),
        topics=extract_topics(segments),
        entities=extract_entities(segments, text),
    )
    if not config.parse_dates:
        result.entities.dates.clear()
    total = (
        _handle_group("participant_extractor", result.participants, config, result)
        + _handle_group("decision_extractor", result.decisions, config, result)
        + _handle_group("commitment_extractor", result.commitments, config, result)
        + _handle_group("task_extractor", result.tasks, config, result)
        + _handle_group("question_extractor", result.open_loops, config, result)
        + _handle_group("dependency_extractor", result.dependencies, config, result)
        + _handle_group("risk_extractor", result.risks, config, result)
        + _handle_group("action_item_extractor", result.action_items, config, result)
        + _handle_group("topic_extractor", result.topics, config, result)
    )
    if config.strict and total == 0:
        raise EmptyTranscriptError("strict mode: no records extracted")
    return result
