"""Configuration for the deterministic extraction pipeline."""

from dataclasses import dataclass, field

from organizational_memory.extraction.errors import InvalidExtractionConfigError

ALL_EXTRACTORS: frozenset[str] = frozenset(
    {
        "participant_extractor",
        "decision_extractor",
        "commitment_extractor",
        "task_extractor",
        "question_extractor",
        "dependency_extractor",
        "risk_extractor",
        "action_item_extractor",
        "topic_extractor",
    }
)


@dataclass(frozen=True)
class ExtractionConfig:
    """Tunable, deterministic behavior for the extraction pipeline.

    Attributes:
        min_confidence: Records scoring below this threshold are dropped.
        enabled_extractors: Names of extractors that should run.
        parse_dates: Whether to populate date entities.
        filter_duplicates: Whether to drop duplicate source lines per category.
        strict: Whether to raise when no records are extracted at all.
    """

    min_confidence: float = 0.0
    enabled_extractors: frozenset[str] = field(default=ALL_EXTRACTORS)
    parse_dates: bool = True
    filter_duplicates: bool = True
    strict: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_confidence <= 1.0:
            raise InvalidExtractionConfigError(
                f"min_confidence must be within [0, 1], got {self.min_confidence}"
            )
        unknown = self.enabled_extractors - ALL_EXTRACTORS
        if unknown:
            raise InvalidExtractionConfigError(
                f"unknown extractors: {', '.join(sorted(unknown))}"
            )

    def is_enabled(self, extractor: str) -> bool:
        """Return whether ``extractor`` should run under this configuration."""
        return extractor in self.enabled_extractors


def default_config() -> ExtractionConfig:
    """Return the default extraction configuration."""
    return ExtractionConfig()
