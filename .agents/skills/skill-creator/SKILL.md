---
name: skill-creator
description: Create or improve reusable Codex Skills for construction, engineering, project management, commercial, planning, BIM, and related workflows in this repository.
---

# Construction AI Skill Creator

Use this skill when a repeatable workflow should become a Codex Skill, or when an existing skill needs restructuring.

## Gate before creating a skill
A candidate should normally have:
1. a recognizable recurring task;
2. defined inputs;
3. an ordered workflow;
4. domain checks or calculations;
5. predictable deliverables;
6. QA/QC criteria.

If these are not mature, keep the material as a prompt/reference until the workflow is understood.

## Creation workflow
1. Inspect existing `AI-Prompts/`, skills, references, templates, and scripts for overlap.
2. Define the trigger: when should Codex use this skill?
3. Define required/optional inputs and missing-input behavior.
4. Map the workflow in execution order.
5. Identify calculations, engineering checks, commercial checks, contractual checks, or planning checks.
6. Define which evidence is authoritative and how conflicts are handled.
7. Add references only when they materially help execution.
8. Add scripts only for repeatable deterministic processing/calculation.
9. Define outputs and their minimum content.
10. Define QA/QC and stop/escalation conditions.
11. Test with at least one realistic construction case and one incomplete/ambiguous case.

## Required SKILL.md structure
- Purpose
- Trigger
- Inputs
- Workflow
- Checks / calculations
- References / tools
- Deliverables
- QA/QC
- Stop conditions

## Design principles
Keep the core SKILL.md concise enough to route and execute reliably. Put detailed standards, checklists, examples, and domain references in a `references/` subfolder when useful. Put deterministic utilities in `scripts/`. Avoid duplicating the same rules across multiple skills.

## Safety and professional control
Never represent an AI output as a signed/stamped engineering design or formal professional certification. Flag missing design criteria, governing codes, contradictory source documents, or insufficient evidence rather than fabricating them.
