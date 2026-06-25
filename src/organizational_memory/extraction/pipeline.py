"""End-to-end deterministic extraction pipeline."""

from dataclasses import dataclass, field

from organizational_memory.extraction.action_item_extractor import (
    extract_action_items,
)
from organizational_memory.extraction.commitment_extractor import (
    extract_commitments,
)
from organizational_memory.extraction.decision_extractor import extract_decisions
from organizational_memory.extraction.dependency_extractor import (
    extract_dependencies,
)
from organizational_memory.extraction.entities import (
    ExtractedEntities,
    extract_entities,
)
from organizational_memory.extraction.normalization import normalize_text
from organizational_memory.extraction.participant_extractor import (
    extract_participants,
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


def _as_transcript(source: Transcript | str) -> Transcript:
    if isinstance(source, Transcript):
        return source
    return Transcript(text=source)


def run_extraction(source: Transcript | str) -> ExtractionResult:
    """Run the full deterministic extraction pipeline over ``source``."""
    transcript = _as_transcript(source)
    text = normalize_text(transcript.text)
    segments = segment_text(text)
    return ExtractionResult(
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
