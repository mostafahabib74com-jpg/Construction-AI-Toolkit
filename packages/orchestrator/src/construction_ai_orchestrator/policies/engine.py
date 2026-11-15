"""Schema-aware release policy dispatcher."""

from __future__ import annotations

from typing import Any, Callable

from ..errors import ContractValidationError
from ..validation import SchemaCatalog
from .common import PolicyReport, policy_issue
from .contract import validate_contract_requirement
from .pricing import validate_boq_item, validate_rate
from .quantity import validate_quantity
from .release import validate_deliverable
from .schedule import validate_schedule

QUANTITY = "https://construction-ai-toolkit.dev/contracts/v1/core/quantity.schema.json"
BOQ_ITEM = "https://construction-ai-toolkit.dev/contracts/v1/domain/boq-item.schema.json"
RATE = "https://construction-ai-toolkit.dev/contracts/v1/domain/rate.schema.json"
CONTRACT_REQUIREMENT = "https://construction-ai-toolkit.dev/contracts/v1/domain/contract-requirement.schema.json"
SCHEDULE = "https://construction-ai-toolkit.dev/contracts/v1/domain/schedule.schema.json"
DELIVERABLE = "https://construction-ai-toolkit.dev/contracts/v1/domain/deliverable.schema.json"


class AccuracyPolicyEngine:
    def __init__(self, catalog: SchemaCatalog) -> None:
        self.catalog = catalog
        self._validators: dict[str, Callable[[dict[str, Any]], list[dict[str, Any]]]] = {
            QUANTITY: validate_quantity,
            BOQ_ITEM: validate_boq_item,
            RATE: validate_rate,
            CONTRACT_REQUIREMENT: validate_contract_requirement,
            SCHEDULE: validate_schedule,
            DELIVERABLE: validate_deliverable,
        }

    def evaluate(self, schema_id: str, payload: Any) -> PolicyReport:
        self.catalog.assert_valid(payload, schema_id)
        validator = self._validators.get(schema_id)
        return PolicyReport(tuple(validator(payload) if validator else ()))

    def evaluate_release_artifact(self, artifact: dict[str, Any]) -> PolicyReport:
        if artifact.get("status") not in {"validated", "conditionally_approved", "approved"}:
            return PolicyReport()
        issues: list[dict[str, Any]] = []
        schema_id = artifact.get("schema_id")
        schema_version = artifact.get("schema_version")
        artifact_status = artifact.get("status")
        review = artifact.get("review") or {}
        if artifact_status == "approved" and (
            review.get("status") != "approved" or not review.get("reviewed_by")
        ):
            issues.append(policy_issue(
                "ARTIFACT_APPROVAL_MISSING",
                "An approved artifact requires an approved review with an identified reviewer.",
                path="$.review",
                remediation="Record the authorized professional review before final release.",
            ))
        if artifact_status == "conditionally_approved" and review.get("status") != "conditionally_approved":
            issues.append(policy_issue(
                "ARTIFACT_CONDITIONAL_APPROVAL_MISSING",
                "A conditionally approved artifact requires a matching review record.",
                path="$.review",
                remediation="Record the conditional approval and its conditions.",
            ))
        if not schema_id:
            issues.append(policy_issue(
                "ARTIFACT_SCHEMA_MISSING",
                "A validated or approved artifact requires a canonical schema ID.",
                path="$.schema_id",
                remediation="Assign a known canonical schema and validate its payload.",
            ))
        if not schema_version:
            issues.append(policy_issue(
                "ARTIFACT_SCHEMA_VERSION_MISSING",
                "A validated or approved artifact requires a schema version.",
                path="$.schema_version",
                remediation="Record the canonical schema version used for validation.",
            ))
        if "payload" not in artifact or artifact.get("payload") is None:
            issues.append(policy_issue(
                "ARTIFACT_PAYLOAD_MISSING",
                "A validated or approved artifact requires an inline payload for validation.",
                path="$.payload",
                remediation="Provide the canonical payload before release validation.",
            ))
        if issues:
            return PolicyReport(tuple(issues))
        if schema_id not in self.catalog.schema_ids:
            return PolicyReport((policy_issue(
                "ARTIFACT_SCHEMA_UNKNOWN",
                "The artifact references an unknown canonical schema.",
                path="$.schema_id",
                remediation="Use a schema ID from the local canonical catalog.",
                details={"schema_id": schema_id},
            ),))
        try:
            report = self.evaluate(schema_id, artifact["payload"])
        except ContractValidationError as exc:
            return PolicyReport((policy_issue(
                "ARTIFACT_PAYLOAD_SCHEMA_INVALID",
                "The artifact payload does not conform to its canonical schema.",
                path="$.payload",
                remediation="Correct the payload before release.",
                details=exc.details,
            ),))
        prefixed = []
        for issue in report.issues:
            updated = dict(issue)
            updated["path"] = issue["path"].replace("$", "$.payload", 1)
            prefixed.append(updated)
        return PolicyReport(tuple(prefixed))
