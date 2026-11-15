"""Create an explicit, separate synthetic project on user request only."""

from __future__ import annotations

import json
from construction_ai_scheduling.domain.estimating import empty_estimate


def create_demo(services, repo_root):
    samples = repo_root / "apps/scheduling-mvp/sample_data"
    project_data = json.loads((samples / "sample_project.json").read_text(encoding="utf-8"))
    schedule_data = json.loads((samples / "milestone_2_demo_schedule.json").read_text(encoding="utf-8"))
    project = services.project.create_project(project_data["project_input"])
    workspace = services.workspace.ensure_for_project(project.project_id)
    nodes = {}
    for item in schedule_data["wbs"]:
        node = services.wbs.save(schedule_id=workspace.schedule_id, code=item["code"], name=item["name"],
                                 parent_wbs_id=nodes.get(item["parent_code"]), sort_order=item["sort_order"])
        nodes[item["code"]] = node.wbs_id
    calendar = services.calendar.save(schedule_id=workspace.schedule_id, **schedule_data["calendar"])
    activities = {}
    for item in schedule_data["activities"]:
        values = {key: value for key, value in item.items() if key != "wbs_code"}
        activity = services.activity.save(schedule_id=workspace.schedule_id, **values,
                    wbs_id=nodes[item["wbs_code"]], calendar_id=calendar.calendar_id,
                    notes="Synthetic demonstration only; not for construction.", assumptions=[])
        activities[item["activity_id"]] = activity.activity_pk
    for item in schedule_data["relationships"]:
        services.relationship.save(schedule_id=workspace.schedule_id,
            predecessor_activity_pk=activities[item["predecessor"]], successor_activity_pk=activities[item["successor"]],
            relationship_type=item["type"], lag_hours=item["lag_hours"])
    services.schedule.calculate(workspace.schedule_id)
    estimate = empty_estimate()
    estimate["demonstration_data"] = True
    estimate["items"] = [{"item_id": "DEMO-COST-01", "description": "بند تجريبي لاختبار الحساب فقط", "unit": "unit",
        "quantity": "10", "quantity_source": "Synthetic demonstration; not measured project data", "resources": [
            {"name": "Synthetic material", "category": "material", "resource_unit": "unit", "consumption": "1", "rate": "80", "waste_percent": "0", "waste_basis": "", "source": "Synthetic arithmetic example, not a quotation", "price_date": "2026-01-01", "currency": project.currency},
            {"name": "Synthetic crew", "category": "labor", "resource_unit": "crew-hour", "consumption": "1", "rate": "20", "waste_percent": "0", "waste_basis": "", "source": "Synthetic arithmetic example, not a wage", "price_date": "2026-01-01", "currency": project.currency},
        ]}]
    estimate["commercial"]["profit_percent"] = "25"
    services.schedule.repository.save_estimate_draft(project.project_id, estimate)
    return project
