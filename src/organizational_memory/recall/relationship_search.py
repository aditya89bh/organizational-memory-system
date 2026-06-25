"""Deterministic search over EntityRelationship records.

Relationships are not persisted in the Phase 4 stores, so this search operates
over an explicit iterable of :class:`EntityRelationship` records (for example,
relationships derived during extraction or held in memory).
"""

from collections.abc import Iterable

from organizational_memory.models import EntityRelationship, RelationshipType
from organizational_memory.recall.engine import RecallResult
from organizational_memory.recall.filters import status_matches


def search_relationships(
    relationships: Iterable[EntityRelationship],
    *,
    source_type: str | None = None,
    source_id: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    relationship_type: RelationshipType | str | None = None,
    related_id: str | None = None,
) -> list[RecallResult]:
    """Return relationships matching the given filters, ordered by id.

    ``related_id`` matches when either endpoint references that entity id; the
    remaining arguments are exact-match filters on the endpoints and type.
    """
    matches: list[EntityRelationship] = []
    for relationship in relationships:
        if source_type is not None and relationship.source.entity_type != source_type:
            continue
        if source_id is not None and relationship.source.entity_id != source_id:
            continue
        if target_type is not None and relationship.target.entity_type != target_type:
            continue
        if target_id is not None and relationship.target.entity_id != target_id:
            continue
        if not status_matches(relationship.relationship_type, relationship_type):
            continue
        if related_id is not None and related_id not in (
            relationship.source.entity_id,
            relationship.target.entity_id,
        ):
            continue
        matches.append(relationship)

    matches.sort(key=lambda relationship: relationship.id)
    return [
        RecallResult(
            record=relationship,
            score=1.0,
            details={
                "relationship_type": relationship.relationship_type.value,
                "source": f"{relationship.source.entity_type}:"
                f"{relationship.source.entity_id}",
                "target": f"{relationship.target.entity_type}:"
                f"{relationship.target.entity_id}",
            },
        )
        for relationship in matches
    ]
