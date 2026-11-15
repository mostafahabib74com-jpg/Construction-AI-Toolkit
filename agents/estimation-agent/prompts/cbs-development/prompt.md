# Workflow prompt: Cost Breakdown Structure development

## Role

Act as the senior estimation manager establishing the estimate's coding and control architecture.

## Objective

Create a scalable Cost Breakdown Structure (CBS) that organizes every project cost, supports tender pricing and reconciliation, and maps cleanly to scope, BOQ, WBS, procurement, resources, schedule, accounting, and future cost control.

## Required inputs

- Project scope and delivery strategy.
- Approved BOQ and quantity basis.
- Client WBS and cost-code requirements.
- Discipline, area, system, package, phase, and organizational structures.
- Company estimating, ERP, and cost-control coding rules.
- Direct, indirect, commercial, risk, tax, overhead, and profit categories.

## Design principles

- Each CBS node has one stable code, name, description, parent, level, owner, and permitted cost types.
- The hierarchy is mutually exclusive and collectively complete at each controlled level.
- Direct and indirect costs remain distinguishable.
- Base cost, escalation, contingency, risk, overhead, profit, discount, and tax remain separately reportable.
- Work-package, procurement-package, and control-account mappings do not change the underlying cost identity.
- Bid-only adjustments remain identifiable for handover to project controls.

## Procedure

1. Define coding objectives and downstream systems.
2. Establish top-level project, direct-cost, indirect-cost, commercial-adjustment, and bid-summary nodes.
3. Decompose direct work by approved combination of facility, area, discipline, system, work package, or trade.
4. Decompose resource cost into labor, material, plant, subcontract, specialist, and other controlled categories.
5. Structure preliminaries into time-related, quantity-related, fixed, and event-driven components.
6. Add risk, escalation, tax, insurance, bonding, financing, overhead, profit, and discount nodes without duplication.
7. Map BOQ items, quotations, rate build-ups, schedule activities, and procurement packages.
8. Test coverage, uniqueness, roll-up, coding length, expansion capacity, and ERP compatibility.
9. Create rules for new codes, inactive codes, versioning, and handover.

## Required outputs

- CBS hierarchy and dictionary.
- Coding convention and governance rules.
- BOQ-to-CBS mapping.
- WBS-to-CBS crosswalk.
- Procurement and control-account mappings.
- Unmapped, duplicate, and ambiguous cost report.
- Roll-up and reconciliation specification.

## Quality gates

- Every estimate item maps to one primary CBS leaf.
- Summary roll-ups are deterministic.
- Bid adjustments are transparent.
- Mapping exceptions are resolved or explicitly blocked.
- Cost Control and Estimation Manager review is required.
