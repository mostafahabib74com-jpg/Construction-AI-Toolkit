"""Deterministic structural and logic checks for canonical schedules."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from .common import policy_issue


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def _has_cycle(nodes: set[str], edges: dict[str, set[str]]) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(successor) for successor in edges.get(node, set())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in nodes if node not in visited)


def _parse_date_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_schedule(value: dict[str, Any], *, excessive_lag_hours: float = 80.0) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    wbs = value.get("wbs") or []
    activities = value.get("activities") or []
    calendars = value.get("calendars") or []

    wbs_ids = [item["wbs_id"] for item in wbs]
    for duplicate in _duplicates(wbs_ids):
        issues.append(policy_issue(
            "WBS_ID_DUPLICATE",
            f"WBS ID '{duplicate}' is duplicated.",
            path="$.wbs",
            remediation="Assign a unique WBS ID.",
            details={"wbs_id": duplicate},
        ))
    wbs_set = set(wbs_ids)
    wbs_edges: dict[str, set[str]] = defaultdict(set)
    levels = {item["wbs_id"]: item["level"] for item in wbs}
    for index, item in enumerate(wbs):
        parent = item.get("parent_wbs_id")
        if parent and parent not in wbs_set:
            issues.append(policy_issue(
                "WBS_PARENT_MISSING",
                f"Parent WBS '{parent}' does not exist.",
                path=f"$.wbs[{index}].parent_wbs_id",
                remediation="Create the parent node or correct the reference.",
            ))
        elif parent:
            wbs_edges[parent].add(item["wbs_id"])
            if levels[item["wbs_id"]] != levels[parent] + 1:
                issues.append(policy_issue(
                    "WBS_LEVEL_INCONSISTENT",
                    "WBS level is inconsistent with its parent.",
                    path=f"$.wbs[{index}].level",
                    remediation="Set the child level to parent level plus one.",
                    severity="warning",
                ))
    if _has_cycle(wbs_set, wbs_edges):
        issues.append(policy_issue(
            "WBS_CYCLE",
            "The WBS parent-child structure contains a cycle.",
            path="$.wbs",
            remediation="Remove the circular parent relationship.",
        ))

    calendar_ids = [item["calendar_id"] for item in calendars]
    for duplicate in _duplicates(calendar_ids):
        issues.append(policy_issue(
            "CALENDAR_ID_DUPLICATE",
            f"Calendar ID '{duplicate}' is duplicated.",
            path="$.calendars",
            remediation="Assign a unique calendar ID.",
        ))
    calendar_set = set(calendar_ids)

    activity_ids = [item["activity_id"] for item in activities]
    for duplicate in _duplicates(activity_ids):
        issues.append(policy_issue(
            "ACTIVITY_ID_DUPLICATE",
            f"Activity ID '{duplicate}' is duplicated.",
            path="$.activities",
            remediation="Assign a unique activity ID.",
        ))
    activity_set = set(activity_ids)
    logic_edges: dict[str, set[str]] = defaultdict(set)
    predecessors: dict[str, set[str]] = defaultdict(set)
    successors: dict[str, set[str]] = defaultdict(set)
    for index, activity in enumerate(activities):
        activity_id = activity["activity_id"]
        if activity["wbs_id"] not in wbs_set:
            issues.append(policy_issue(
                "ACTIVITY_WBS_MISSING",
                f"Activity '{activity_id}' references an unknown WBS.",
                path=f"$.activities[{index}].wbs_id",
                remediation="Assign the activity to an existing WBS node.",
            ))
        if activity["calendar_id"] not in calendar_set:
            issues.append(policy_issue(
                "ACTIVITY_CALENDAR_MISSING",
                f"Activity '{activity_id}' references an unknown calendar.",
                path=f"$.activities[{index}].calendar_id",
                remediation="Assign an existing, reviewed calendar.",
            ))
        if activity["activity_type"] in {"start_milestone", "finish_milestone"} and activity["duration_hours"] != 0:
            issues.append(policy_issue(
                "MILESTONE_DURATION_NONZERO",
                f"Milestone '{activity_id}' must have zero duration.",
                path=f"$.activities[{index}].duration_hours",
                remediation="Set milestone duration to zero.",
            ))
        start = activity.get("planned_start")
        finish = activity.get("planned_finish")
        if start and finish and _parse_date_time(finish) < _parse_date_time(start):
            issues.append(policy_issue(
                "ACTIVITY_DATES_REVERSED",
                f"Activity '{activity_id}' finishes before it starts.",
                path=f"$.activities[{index}].planned_finish",
                remediation="Correct the dates and recalculate the schedule.",
            ))
        for relation_index, relation in enumerate(activity.get("relationships") or []):
            predecessor = relation["predecessor_activity_id"]
            relation_path = f"$.activities[{index}].relationships[{relation_index}]"
            if predecessor not in activity_set:
                issues.append(policy_issue(
                    "RELATIONSHIP_ENDPOINT_MISSING",
                    f"Relationship predecessor '{predecessor}' does not exist.",
                    path=f"{relation_path}.predecessor_activity_id",
                    remediation="Correct or remove the relationship.",
                ))
                continue
            if predecessor == activity_id:
                issues.append(policy_issue(
                    "RELATIONSHIP_SELF_REFERENCE",
                    f"Activity '{activity_id}' cannot depend on itself.",
                    path=f"{relation_path}.predecessor_activity_id",
                    remediation="Remove the self-reference.",
                ))
            logic_edges[predecessor].add(activity_id)
            predecessors[activity_id].add(predecessor)
            successors[predecessor].add(activity_id)
            lag = relation["lag_hours"]
            if lag < 0:
                issues.append(policy_issue(
                    "RELATIONSHIP_NEGATIVE_LAG",
                    "Negative lag requires planner review.",
                    path=f"{relation_path}.lag_hours",
                    remediation="Replace leads with explicit activities where practical, or document approval.",
                    severity="warning",
                ))
            if abs(lag) > excessive_lag_hours:
                issues.append(policy_issue(
                    "RELATIONSHIP_EXCESSIVE_LAG",
                    f"Lag exceeds the {excessive_lag_hours:g}-hour review threshold.",
                    path=f"{relation_path}.lag_hours",
                    remediation="Model the waiting period explicitly or document the basis.",
                    severity="warning",
                ))
    if _has_cycle(activity_set, logic_edges):
        issues.append(policy_issue(
            "SCHEDULE_LOGIC_CYCLE",
            "Activity relationships contain a circular dependency.",
            path="$.activities",
            remediation="Remove the circular relationship and rerun CPM calculations.",
        ))
    for index, activity in enumerate(activities):
        activity_id = activity["activity_id"]
        if not predecessors[activity_id] and activity["activity_type"] != "start_milestone":
            issues.append(policy_issue(
                "ACTIVITY_OPEN_START",
                f"Activity '{activity_id}' has no predecessor.",
                path=f"$.activities[{index}].relationships",
                remediation="Connect it to the project start or document the exception.",
                severity="warning",
            ))
        if not successors[activity_id] and activity["activity_type"] != "finish_milestone":
            issues.append(policy_issue(
                "ACTIVITY_OPEN_FINISH",
                f"Activity '{activity_id}' has no successor.",
                path=f"$.activities[{index}]",
                remediation="Connect it to a completion milestone or document the exception.",
                severity="warning",
            ))
    return issues
