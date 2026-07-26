# Estimation Agent

The Estimation Agent is the first specialized agent in Construction-AI-Toolkit's AI Engineering Platform. It supports the controlled tender-estimating lifecycle from RFP intake through final bid-package readiness.

## Mission

Produce complete, competitive, traceable, and professionally reviewable construction estimates and bid deliverables without inventing scope, quantities, rates, quotations, contract requirements, or approvals.

## Supported capabilities

1. RFP document analysis.
2. Project scope extraction.
3. Missing-information and ambiguity detection.
4. Technical RFI generation.
5. Commercial query generation.
6. Design Basis Report preparation.
7. BOQ development.
8. Cost Breakdown Structure development.
9. Excel cost-model specification and workbook-generation instructions.
10. Subcontractor and supplier quotation comparison.
11. Pricing-risk assessment.
12. Technical proposal preparation.
13. Commercial proposal preparation.
14. Final bid-package assembly and readiness review.

## Operating principles

- Source evidence is cited at document, page, clause, drawing, sheet, cell, or revision level whenever available.
- Missing data remains visible; it is never silently replaced with invented facts.
- Arithmetic, unit conversions, pricing extensions, markups, and reconciliations require deterministic calculation tools when implemented.
- Every estimate records its basis, assumptions, exclusions, qualifications, pricing date, currency, unit system, tax treatment, escalation, contingency, and approval status.
- Client-issued, company-approved, calculated, assumed, and AI-recommended information remain distinguishable.
- Technical and commercial outputs require qualified human review before issue.

## Maturity

This milestone provides the complete agent specification, prompts, workflow contracts, review controls, knowledge profiles, examples, and evaluation requirements. Runtime parsers, calculation engines, workbook generators, and external integrations are intentionally not implemented yet.

## Directory map

```text
estimation-agent/
├── agent.yaml
├── knowledge/
├── prompts/
│   ├── system.md
│   ├── shared/
│   └── <workflow-id>/prompt.md
├── schemas/
├── workflows/
│   └── <workflow-id>/
├── templates/
│   └── excel-cost-model/
├── tools/
├── evaluations/
├── examples/
└── docs/
```

See `docs/workflow-catalog.md` for the workflow sequence and handoffs.
