# Tender Manager Agent architecture

## Position in the platform

The agent is a tender-control orchestrator. It converts controlled tender sources and approved contributor artifacts into coordinated submission deliverables. It is not the authoritative calculator for estimate, quantity, schedule, BIM, QA/QC, HSE, contract, tax, or engineering results.

```text
Tender package + addenda + portal rules
                 |
      document and revision control
                 |
 requirements -> owners -> responses -> evidence
                 |
 approved domain-agent and company artifacts
                 |
 technical + commercial + forms + registers
                 |
 deterministic validation and reconciliations
                 |
 professional reviews -> executive authorization
                 |
       controlled submission package
```

## Control planes

- Evidence plane: sources, revisions, addenda, clauses, pages, sheets, files, and extraction quality.
- Requirement plane: mandatory, scored, informational, contractual, commercial, technical, portal, and form requirements.
- Contribution plane: owners, due dates, versions, review state, comments, and approved upstream artifacts.
- Proposal plane: section outlines, response content, evidence, cross-references, graphics specifications, and page limits.
- Commercial plane: price schedules, currencies, taxes, qualifications, assumptions, exclusions, forms, securities, and reconciliations.
- Submission plane: naming, formats, encryption, signatures, file sizes, envelopes, portal fields, packaging, checksums, approvals, and deadline controls.

## Cross-agent boundaries

- Estimation Agent owns validated estimate totals, pricing basis, and commercial proposal source data.
- Planning & P6 Agent owns schedule dates, logic, resource loading, histograms, and schedule exports.
- Quantity Survey Agent owns measurement and quantity artifacts.
- Contract & Claims Agent owns contract-risk and clause-interpretation drafts when implemented.
- BIM, QA/QC, and HSE agents own their reviewed discipline content when implemented.
- Tender Manager Agent owns the requirement matrix, response coordination, proposal assembly, submission manifest, and readiness report.

Conflicts are surfaced as formal reconciliation items. No artifact is silently preferred or overwritten.
