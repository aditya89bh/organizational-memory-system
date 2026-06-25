"""Ownership ranking relative to a target owner identifier.

Scores how strongly a record belongs to a given owner, checking (in order of
strength) the record owner, the acting actor, meeting participants, and an
explicit ``metadata["assignee"]`` value.
"""

from organizational_memory.schemas.base import BaseRecord

_OWNER_SCORE = 1.0
_ACTOR_SCORE = 0.9
_PARTICIPANT_SCORE = 0.7
_ASSIGNEE_SCORE = 0.6


def ownership_score(record: BaseRecord, owner: str | None) -> float:
    """Return an ownership score in ``[0, 1]`` for ``record`` and ``owner``.

    Returns ``0.0`` when ``owner`` is ``None`` or no ownership signal matches.
    """
    if owner is None:
        return 0.0

    if getattr(record, "owner_id", None) == owner:
        return _OWNER_SCORE
    if getattr(record, "actor_id", None) == owner:
        return _ACTOR_SCORE

    participants = getattr(record, "participants", None)
    if isinstance(participants, list) and owner in participants:
        return _PARTICIPANT_SCORE

    metadata = getattr(record, "metadata", {})
    if isinstance(metadata, dict) and metadata.get("assignee") == owner:
        return _ASSIGNEE_SCORE

    return 0.0
