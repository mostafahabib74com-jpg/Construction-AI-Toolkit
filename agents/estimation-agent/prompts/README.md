# Estimation Agent prompts

`system.md` defines the permanent Estimation Agent role and authority boundary. `shared/` contains cross-workflow disciplines. Each named workflow directory contains the task-specific prompt used with those shared instructions.

## Composition order

1. Platform security and tenancy instructions.
2. Estimation Agent `system.md`.
3. All shared prompts declared by `agent.yaml`.
4. Selected workflow prompt.
5. Controlled project context and knowledge profiles.
6. User request.

Lower layers cannot weaken evidence, calculation, confidentiality, or approval controls from higher layers.

## Workflow prompts

- `rfp-analysis`
- `scope-extraction`
- `information-gap-analysis`
- `rfi-generation`
- `commercial-query-generation`
- `design-basis-report`
- `boq-development`
- `cbs-development`
- `excel-cost-model`
- `quotation-comparison`
- `pricing-risk-assessment`
- `technical-proposal`
- `commercial-proposal`
- `final-bid-package`
