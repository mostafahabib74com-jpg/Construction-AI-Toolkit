# Legacy tender prompt migration

Legacy files under `AI-Prompts/Tendering/` remain educational material. Their intent maps to controlled workflows as follows.

| Legacy prompt | Controlled destination | Required upgrade |
|---|---|---|
| Tender document review | `tender-package-ingestion` + `compliance-matrix` | Full register, revisions, addenda, deadlines, completeness, atomic requirements, evidence |
| BOQ analysis | Estimation/Quantity Survey approved artifacts + `commercial-proposal` | Deterministic quantity/price ownership and reconciliation |
| Technical proposal | `technical-proposal` | Requirement mapping, approved artifacts, verified claims, section reviews, rendering specification |
| Commercial proposal | `commercial-proposal` | Approved estimate version, forms, tax/terms, assumptions/exclusions/deviations, total reconciliation |
| Risk assessment | Domain risk artifacts + assumptions/exclusions/clarification workflows | Source, owner, treatment, approval, proposal impact |
| RFI generator | `clarification-management` + `rfi-generation` | Duplicate checks, authority, commercial safety, issue/response history, impact propagation |
| Method statement | `execution-methodology` and future QA/QC/HSE workflows | Constructability, schedule/resources, quality/safety controls, discipline review |
| Execution plan | `execution-methodology`, `organization-chart`, resource, and schedule workflows | Integrated governance, methods, logistics, schedule, resources, interfaces |
| Bid/no-bid decision | Future governance workflow; AI recommendation only | Authority matrix, strategic/commercial risk, executive decision record |
| Final bid review | `submission-package` | Immutable manifest, exact-version approvals, compliance, forms/signatures, preflight, security, readiness |

Do not copy a legacy prompt directly into orchestration. Bind its valid intent to the agent system/shared prompts, controlled knowledge, schemas, workflow authority, and named reviewers. This milestone does not delete or rewrite legacy files.
