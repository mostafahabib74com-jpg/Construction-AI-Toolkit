# Using Construction AI Toolkit with Codex

This repository now includes repository-scoped Codex Skills under `.agents/skills/`.

## Start Codex in the repository

Clone and enter the repository, then start Codex from inside it:

```bash
git clone https://github.com/mostafahabib74com-jpg/Construction-AI-Toolkit.git
cd Construction-AI-Toolkit
git checkout codex-skills-foundation
codex
```

Codex can discover repository skills placed under `.agents/skills/` and repository instructions in `AGENTS.md`.

## Explicit skill invocation

Try:

```text
$tender-management
Review the tender documents in this workspace, create a document register, reconcile the BOQ against the scope/specifications/drawings, identify clarifications and commercial risks, then prepare the bid-review outputs defined by the skill.
```

For skill creation:

```text
$skill-creator
Convert our repeatable construction rate-analysis workflow into a new Codex Skill. First inspect existing prompts and skills, then propose the trigger, inputs, ordered workflow, checks, outputs, QA/QC, references, and tests.
```

## Implicit skill selection test

Without naming the skill, ask:

```text
Review this construction tender end-to-end. Do not rely on the BOQ alone. Cross-check all drawings, specifications, conditions, schedules, appendices, and clarifications, then identify gaps, RFIs, risks, pricing assumptions, and final bid checks.
```

Codex should select `tender-management` when the task matches its description.

## Validation checklist

Confirm that:
1. Codex sees the repository-level `AGENTS.md`.
2. `$tender-management` is available for explicit invocation.
3. `$skill-creator` is available for explicit invocation.
4. Tender-management loads its instructions only when selected.
5. References/scripts are only read or executed when needed.
6. The skill refuses to invent missing quantities, rates, clauses, or project data.
7. The skill clearly separates source facts from assumptions and clarifications.

If newly added skills do not appear, restart Codex and test again.
