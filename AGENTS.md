# Construction AI Toolkit — Codex Agent Instructions

## Mission
Use this repository as a construction-engineering AI system, not merely a prompt collection. Preserve the existing `AI-Prompts/` library and use it as reference material while progressively building reusable Codex Skills under `.agents/skills/`.

## Operating rules
1. Read the relevant project/tender/source files before drawing conclusions.
2. Never invent missing quantities, rates, contract clauses, drawing data, approvals, codes, or client requirements.
3. Separate facts, assumptions, clarifications, exclusions, risks, calculations, and recommendations.
4. Cross-check BOQ, drawings, specifications, conditions, addenda, schedules, and clarifications whenever they exist.
5. Keep calculations traceable and state units, formulas, sources, and assumptions.
6. For Saudi projects, account for project-specific Saudi requirements only when supported by the tender documents or an authoritative reference.
7. Treat engineering, commercial, contractual, planning, BIM, and document-production workflows as connected disciplines.
8. Preserve source files. Do not overwrite original tender/project evidence unless explicitly requested.
9. Prefer reusable workflows, references, scripts, templates, and validation checks over one-off prompts.
10. Before final delivery, perform discipline-specific QA/QC.

## Codex Skills architecture
Repository skills live under:

`.agents/skills/<skill-name>/SKILL.md`

Keep each discoverable skill as its own direct child folder under `.agents/skills/`. Use names such as `tender-management`, `quantity-takeoff`, `structural-analysis`, `rc-column-design`, `foundation-design`, `etabs-workflow`, and `safe-workflow`.

A skill should define:
- purpose and trigger conditions;
- required and optional inputs;
- ordered workflow;
- calculations/checks;
- tool and script usage;
- references/templates;
- output contract;
- QA/QC and stop conditions.

Do not create a new skill merely because a prompt exists. Create a skill when a repeatable workflow has a clear trigger, inputs, process, checks, and deliverables.

## Initial skill roadmap
- skill-creator
- tender-management
- quantity-takeoff
- rate-analysis
- construction-estimating
- contract-management
- primavera-p6
- project-controls
- construction-management
- bim-management
- structural-analysis
- rc-design
- rc-column-design
- rc-beam-design
- rc-slab-design
- foundation-design
- retaining-wall-design
- structural-repair
- etabs-workflow
- safe-workflow
- structural-drawing-review
- structural-shop-drawings

## Skill routing
When a task spans disciplines, coordinate skills rather than forcing one skill to do everything. A tender may require tender-management + quantity-takeoff + rate-analysis + construction-estimating + contract-management + primavera-p6.

## Legacy prompt library
`AI-Prompts/` remains valid reference material. Skills may reference it, but should improve it into a deterministic workflow with validation rather than simply copy prompt text.
