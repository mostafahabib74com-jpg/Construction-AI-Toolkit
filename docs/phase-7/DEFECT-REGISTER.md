# Phase 7 defect register

Severity: P0 blocks any integrated execution; P1 blocks a required Phase 7 objective; P2 causes material inconsistency or weak assurance; P3 is documentation/debt.

| ID | Priority | Defect | Evidence | Recommended disposition |
|---|---|---|---|---|
| INT-001 | P0 | No central orchestrator or executable workflow runtime | Architecture describes orchestration; no `apps/` or `packages/` runtime exists | Implement neutral orchestrator after architecture approval |
| INT-002 | P0 | No shared canonical data schemas | Three independent common schemas; requested shared entities absent | Add `packages/contracts/schemas` and compatibility mappings |
| INT-003 | P1 | Global workflow IDs are ambiguous | `rfi-generation`, `technical-proposal`, and `commercial-proposal` each exist in two agents | Route by `agent_id/workflow_id`; reject ambiguous aliases |
| INT-004 | P1 | Final bid-package ownership conflicts | Estimation `final-bid-package` overlaps Tender `submission-package` | Make Estimation output an estimate release; Tender owns final assembly/readiness |
| INT-005 | P1 | Tender agent name/ID conflicts with architecture | `tender-proposal-agent` versus implemented `tender-manager-agent` | Choose canonical ID and add alias/migration note; recommend implemented ID |
| INT-006 | P1 | No build, dependency, or runtime manifest | No Python/Node/package/lock manifest found | Add versioned Python project and lock strategy |
| INT-007 | P1 | No executable automated tests or CI | No test files, test runner, or workflow found | Add pytest suite and GitHub Actions checks |
| INT-008 | P1 | Evaluation declarations are not executable | 39 case descriptions; zero reviewed expected artifacts | Add fixtures, expected outputs, scoring runner, and regression gates |
| INT-009 | P1 | No JSON Schema/YAML validation tool in repository | Static parsing only; no declared validator dependency | Add Draft 2020-12 and YAML validators |
| INT-010 | P1 | Deterministic engineering services are absent | Tools are documentation-only | Add adapters/interfaces, then implement in risk order |
| INT-011 | P1 | Excel generation is specification-only | Workbook specification exists; no generator or `.xlsx` test | Implement controlled workbook generator and formula/render tests |
| INT-012 | P1 | P6 output capability is specification-only | XER/XML formats declared; adapter and round-trip validator absent | Return `not_implemented` until validated P6 service exists |
| INT-013 | P1 | No consolidated-result contract | Each agent has independent output envelope | Add shared orchestration result and artifact manifest schemas |
| INT-014 | P1 | Missing-data and error behavior is not executable | Prompts describe blockers; no runtime error model | Add standard error/blocker schema and tests |
| INT-015 | P2 | Common source schemas are incompatible | `documentReference`/`sourceReference`, differing dates/status/checksum | Introduce canonical source/evidence schema plus adapters |
| INT-016 | P2 | Finding/register/review enums drift | Domain schemas use incompatible required fields and statuses | Define core vocabularies with domain extension fields |
| INT-017 | P2 | Project/tender metadata is inconsistent | Different project, cutoff, language, currency, unit, and time fields | Add canonical project/opportunity/tender metadata schemas |
| INT-018 | P2 | Prompt structure is inconsistent | Three different section conventions | Adopt one eight-section prompt format and lint it |
| INT-019 | P2 | Machine-readable workflow catalog is inconsistent | Estimation alone has `workflows/catalog.yaml` | Central registry should discover all manifests/contracts; deprecate private catalog later |
| INT-020 | P2 | Knowledge/standards governance differs | Estimation alone has a standards register | Add shared knowledge-profile contract and validation |
| INT-021 | P2 | Output formats can be misread as implemented | Manifests list office/P6/package formats despite absent handlers | Add capability states: declared, available, validated |
| INT-022 | P2 | No end-to-end demonstration | Only one input/output example per agent | Add synthetic project pipeline with golden outputs |
| INT-023 | P2 | No agent-to-agent artifact registry | Tender defines local artifact references; other agents do not | Add shared immutable artifact schema/store interface |
| INT-024 | P2 | No executable safeguards for quantities/prices/schedules/mandatory fields | Safety exists only in prompts/schemas | Add policy validators and negative tests |
| INT-025 | P2 | All workflows remain specification status | 44 of 44 workflow files declare `specification` | Promote only tested handlers through maturity gates |
| INT-026 | P2 | Roadmap is stale | Root roadmap still describes unfinished early prompt-library work | Update after Phase 7 architecture is accepted |
| INT-027 | P2 | Seven planned initial agents are absent | Architecture defines ten agents; three implemented | Track separately; do not block integration of current three |
| INT-028 | P3 | Legacy and platform naming conventions differ | Numbered uppercase/special-character legacy paths vs kebab-case agent paths | Preserve legacy namespace; lint new platform paths only |
| INT-029 | P3 | Development-state messaging is stale/fragmented | Root and legacy tender README say under development; agent docs are more precise | Consolidate status after runtime milestones |
| INT-030 | P3 | Local Git object store contains unreachable blobs | `git fsck` reports dangling blobs, no fatal errors | No source change; allow normal Git maintenance |

## Confirmed non-defects

- No exact duplicate tracked files.
- No duplicate JSON Schema IDs.
- No invalid JSON files.
- No broken checked Markdown or JSON reference targets.
- No missing files inside the 44 five-file workflow packages.
- No deletions are required to begin Phase 7 integration.
