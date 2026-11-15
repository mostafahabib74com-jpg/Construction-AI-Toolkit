# Phase 7 finding classification

## Classification rule

- **Critical:** the integration control plane cannot start, route, exchange, validate, or report a workflow safely.
- **High:** the platform can execute, but engineering accuracy, release confidence, or professional reliability is materially impaired.
- **Medium:** consistency, governance, maintainability, or user clarity should improve after accuracy controls.
- **Optional:** useful future expansion or local maintenance that does not block the current three-agent platform.

Each of the 30 audit findings appears exactly once below. This classification supersedes priority labels only for implementation sequencing; it does not erase the original defect record.

## 1. Critical issues that prevent the platform from working

| Finding | Issue | Corrective action in this milestone |
|---|---|---|
| INT-001 | No central orchestrator or executable workflow runtime | Add a provider-neutral Python orchestrator with registry, router, runner, and CLI. |
| INT-002 | No shared canonical data schemas | Add versioned core and requested domain JSON Schemas. |
| INT-003 | Workflow IDs collide across agents | Use `<agent-id>/<workflow-id>` runtime keys and reject ambiguous unqualified IDs. |
| INT-006 | No build or dependency manifest | Add a Python 3.12 project manifest and reproducible direct dependency lock. |
| INT-009 | No executable YAML/JSON Schema validation | Add YAML loading and Draft 2020-12 JSON Schema validation. |
| INT-013 | No consolidated-result contract | Add canonical workflow-result and consolidated-result schemas and runtime models. |
| INT-014 | Missing-data and error behavior is not executable | Add typed public errors, validation issues, blockers, and safe failure results. |
| INT-023 | No cross-agent artifact registry | Add an immutable in-memory artifact registry and handoff references. |

These changes create the control plane. They do not claim that specification-only agent capabilities are complete.

## 2. High-priority issues that affect accuracy

| Finding | Accuracy impact | Planned corrective action after approval |
|---|---|---|
| INT-004 | Estimation and Tender can both appear to own final bid release | Enforce estimate-release versus submission-package ownership. |
| INT-007 | No complete automated test or CI gate | Add full unit, integration, regression, and CI gates. |
| INT-008 | The 39 evaluations cannot prove behavior | Convert declarations to executable fixtures and expected results. |
| INT-010 | Engineering calculations and document services are absent | Implement deterministic services in risk order. |
| INT-011 | Excel cost models cannot be generated or verified | Build deterministic workbook generation and formula tests. |
| INT-012 | P6 XER/XML outputs cannot be generated or round-trip checked | Add a controlled Primavera adapter and integrity validation. |
| INT-015 | Agent source/evidence models are incompatible | Implement tested legacy-to-canonical adapters. |
| INT-016 | Findings, registers, reviews, and statuses use drifting enums | Govern shared vocabularies and mappings. |
| INT-017 | Project, currency, unit, date, and tender metadata are inconsistent | Apply canonical metadata through adapters. |
| INT-020 | Knowledge and standards governance differs by agent | Add shared standards profiles, applicability, and version checks. |
| INT-024 | Non-invention and schedule/document safeguards exist only in prose | Add quantity, rate, contract, schedule, and release validators with negative tests. |
| INT-025 | All 44 workflows remain specification-only | Implement handlers and promote capabilities only after acceptance tests pass. |

None of these items is implemented in the critical milestone.

## 3. Medium-priority improvements

| Finding | Improvement |
|---|---|
| INT-005 | Canonicalize `tender-manager-agent` and retain `tender-proposal-agent` as a documented alias. |
| INT-018 | Standardize prompt metadata and eight-section prompt structure. |
| INT-019 | Replace inconsistent private catalogs with central discovery and registry reporting. |
| INT-021 | Publish capability maturity as `declared`, `available`, or `validated`. |
| INT-022 | Add a reproducible end-to-end demonstration with golden outputs. |
| INT-026 | Reconcile the root roadmap with implemented agent specifications and runtime maturity. |
| INT-028 | Lint new platform paths while preserving legacy prompt paths. |
| INT-029 | Consolidate development-status messaging across documentation. |

## 4. Optional future enhancements

| Finding | Future action |
|---|---|
| INT-027 | Implement the remaining seven planned agents only after the three-agent platform is integrated and validated. |
| INT-030 | Allow normal Git maintenance to prune unreachable local objects; no source correction is needed. |

## Scope guard

This milestone does not add agents, change agent prompts, implement Excel or Primavera generation, promote any workflow beyond `specification`, or claim production readiness.
