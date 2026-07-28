# Estimation Agent architecture

## Internal flow

```text
Controlled project workspace
        |
Document intake and revision control
        |
RFP requirements -> scope -> gaps -> queries -> approved bid basis
        |
BOQ -> CBS -> quantities/rates/quotations -> deterministic cost model
        |
Pricing risk and authorized commercial adjustments
        |
Technical proposal + commercial proposal
        |
Final reconciliation, approval gates, and bid-package manifest
```

## Components

### Agent definition

`agent.yaml` declares workflows, tools, reviewers, data policy, and prohibited authority.

### Prompt layer

The system prompt establishes permanent behavior. Shared prompts enforce document, evidence, calculation, assumption, presentation, and commercial controls. Workflow prompts supply domain procedures and deliverables.

### Workflow layer

Each workflow is independently versioned and declares prerequisites, inputs, deliverables, tools, blockers, review roles, safety rules, and data contracts.

### Knowledge layer

Knowledge profiles define estimating methodology, information taxonomy, cost taxonomy, pricing risk, and bid governance. Organization, regional, project, and licensed profiles will be supplied at runtime rather than committed as universal truth.

### Deterministic services

Future services will parse documents, normalize units and currencies, calculate quantities and costs, compare quotations, generate workbooks, analyze risk, reconcile totals, and validate packages. Model-generated arithmetic cannot replace these services.

### Evidence layer

All important requirements, scope, quantities, rates, quotations, assumptions, risks, calculations, and bid decisions carry provenance and revision status.

### Review layer

Estimation, commercial, technical, procurement, contracts, finance/tax, and executive reviewers approve the artifacts within their delegated authority. The agent has no approval or submission authority.

## State and versioning

Every workflow execution records agent version, workflow version, prompt composition, model/provider version, tool versions, project/document revision cut-off, input hashes, output artifacts, validation results, reviewer decisions, and supersession status.

Any addendum or late commercial change can invalidate downstream artifacts. Dependency impact must be calculated and affected workflows reopened before final bid readiness.
