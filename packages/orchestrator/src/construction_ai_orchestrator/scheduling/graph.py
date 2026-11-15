"""Deterministic directed-graph functions shared by policy and application code."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable


class GraphCycleError(ValueError):
    def __init__(self, cycle: tuple[str, ...]) -> None:
        super().__init__(f"Directed graph contains a cycle: {' -> '.join(cycle)}")
        self.cycle = cycle


def _adjacency(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> dict[str, tuple[str, ...]]:
    values: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        values[node]
    for predecessor, successor in edges:
        values[predecessor].add(successor)
        values[successor]
    return {node: tuple(sorted(successors)) for node, successors in values.items()}


def find_cycle(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> tuple[str, ...] | None:
    adjacency = _adjacency(nodes, edges)
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> tuple[str, ...] | None:
        if node in visiting:
            first = stack.index(node)
            return tuple(stack[first:] + [node])
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for successor in adjacency.get(node, ()):
            cycle = visit(successor)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(adjacency):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def topological_sort(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> tuple[str, ...]:
    node_set = set(nodes)
    edge_set = set(edges)
    node_set.update(item for edge in edge_set for item in edge)
    cycle = find_cycle(node_set, edge_set)
    if cycle:
        raise GraphCycleError(cycle)

    successors: dict[str, set[str]] = defaultdict(set)
    indegree = {node: 0 for node in node_set}
    for predecessor, successor in edge_set:
        if successor not in successors[predecessor]:
            successors[predecessor].add(successor)
            indegree[successor] += 1
    ready = sorted(node for node, degree in indegree.items() if degree == 0)
    ordered: list[str] = []
    while ready:
        node = ready.pop(0)
        ordered.append(node)
        for successor in sorted(successors.get(node, set())):
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
                ready.sort()
    return tuple(ordered)
