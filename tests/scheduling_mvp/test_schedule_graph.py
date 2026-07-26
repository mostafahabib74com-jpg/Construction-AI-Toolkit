from __future__ import annotations

import pytest

from construction_ai_orchestrator.scheduling.graph import GraphCycleError, find_cycle, topological_sort


def test_topological_sort_is_deterministic():
    assert topological_sort({"C", "B", "A", "D"}, {("A", "C"), ("B", "C")}) == ("A", "B", "C", "D")


def test_cycle_path_is_reported():
    assert find_cycle({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")}) == ("A", "B", "C", "A")
    with pytest.raises(GraphCycleError) as caught:
        topological_sort({"A", "B", "C"}, {("A", "B"), ("B", "C"), ("C", "A")})
    assert caught.value.cycle == ("A", "B", "C", "A")
