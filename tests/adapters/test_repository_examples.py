from __future__ import annotations

import json

from construction_ai_orchestrator.adapters import EstimationAdapter, PlanningAdapter, TenderAdapter


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_estimation_example_maps_without_inventing_time_zone(repo_root, catalog):
    example = read_json(repo_root / "agents/estimation-agent/examples/inputs/synthetic-rfp-context.json")
    adapter = EstimationAdapter(catalog)
    project = adapter.adapt_project(example["project"], time_zone="Asia/Riyadh")
    source = adapter.adapt_source_document(example["documents"][0])
    assert project["project_id"] == "SYNTHETIC-001"
    assert project["time_zone"] == "Asia/Riyadh"
    assert source["document_id"] == "DOC-001"


def test_planning_example_requires_explicit_missing_unit_system(repo_root, catalog):
    example = read_json(repo_root / "agents/planning-p6-agent/examples/inputs/synthetic-wbs-context.json")
    adapter = PlanningAdapter(catalog)
    project = adapter.adapt_project(example["project"], unit_system="SI")
    source = adapter.adapt_source_document(example["documents"][0])
    assert project["unit_system"] == "SI"
    assert project["time_zone"] == "Asia/Riyadh"
    assert source["issue_date"] is None


def test_tender_example_maps_to_explicit_project_context(repo_root, catalog):
    example = read_json(repo_root / "agents/tender-manager-agent/examples/inputs/synthetic-tender-intake.json")
    adapter = TenderAdapter(catalog)
    project = adapter.adapt_tender_project(
        example["tender"],
        project_id="SYN-DEMO-001",
        location="Synthetic City",
        unit_system="SI",
    )
    source = adapter.adapt_source_document(example["documents"][0])
    assert project["tender_id"] == "SYN-TND-001"
    assert project["client"] == "Synthetic Client"
    assert source["controlled_status"] == "current"
    assert source["checksum_algorithm"] == "unspecified"
