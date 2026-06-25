"""Dependency analytics.

Analyzes directed dependencies (``source`` depends on ``target``) to surface
active blockers, blocked records, records that block many others, and dependency
chains. Only non-resolved dependencies are treated as active. Chain discovery is
deterministic and cycle-safe.
"""

from dataclasses import dataclass, field

from organizational_memory.analytics.common import count_by
from organizational_memory.models import Dependency
from organizational_memory.models.enums import DependencyStatus
from organizational_memory.storage.store import MemoryStore

_MAX_CHAINS = 20
_MIN_CHAIN_NODES = 3


@dataclass(frozen=True)
class DependencyReport:
    """Aggregate dependency analytics."""

    total: int
    active_blockers: int
    blocked_records: tuple[str, ...] = ()
    blocking_counts: dict[str, int] = field(default_factory=dict)
    multi_blockers: dict[str, int] = field(default_factory=dict)
    chains: list[tuple[str, ...]] = field(default_factory=list)
    longest_chain: int = 0


def _dependencies(store: MemoryStore) -> list[Dependency]:
    return [r for r in store.list_records("Dependency") if isinstance(r, Dependency)]


def _enumerate_chains(adjacency: dict[str, list[str]]) -> list[tuple[str, ...]]:
    targets = {target for nexts in adjacency.values() for target in nexts}
    roots = sorted(node for node in adjacency if node not in targets)
    chains: list[tuple[str, ...]] = []

    def walk(node: str, path: tuple[str, ...], visited: frozenset[str]) -> None:
        nexts = [n for n in adjacency.get(node, []) if n not in visited]
        if not nexts:
            if len(path) >= _MIN_CHAIN_NODES:
                chains.append(path)
            return
        for nxt in nexts:
            walk(nxt, (*path, nxt), visited | {nxt})

    for root in roots:
        walk(root, (root,), frozenset({root}))

    chains.sort(key=lambda chain: (-len(chain), chain))
    return chains


def dependency_analytics(store: MemoryStore) -> DependencyReport:
    """Compute :class:`DependencyReport` from stored dependencies."""
    dependencies = _dependencies(store)
    active = [
        dep for dep in dependencies if dep.status is not DependencyStatus.RESOLVED
    ]

    blocked_records = tuple(sorted({dep.source_id for dep in active}))
    blocking_counts = count_by(active, lambda dep: dep.target_id)
    multi_blockers = {
        target: count for target, count in blocking_counts.items() if count >= 2
    }

    adjacency: dict[str, list[str]] = {}
    for dep in active:
        adjacency.setdefault(dep.source_id, []).append(dep.target_id)
    for source in adjacency:
        adjacency[source] = sorted(adjacency[source])

    chains = _enumerate_chains(adjacency)
    longest_chain = max((len(chain) for chain in chains), default=0)

    return DependencyReport(
        total=len(dependencies),
        active_blockers=len(active),
        blocked_records=blocked_records,
        blocking_counts=blocking_counts,
        multi_blockers=dict(
            sorted(multi_blockers.items(), key=lambda item: (-item[1], item[0]))
        ),
        chains=chains[:_MAX_CHAINS],
        longest_chain=longest_chain,
    )
