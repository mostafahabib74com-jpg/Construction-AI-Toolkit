# Manual Codex Skills Validation

## Test 1 — Explicit trigger
Invoke `$tender-management` with a folder containing a BOQ plus at least one supporting tender document.

Expected:
- document register first;
- cross-document scope review;
- no BOQ-only pricing assumption;
- visible gaps/clarifications;
- defined deliverables and QA/QC.

## Test 2 — Implicit trigger
Ask for an end-to-end construction tender review without naming the skill.

Expected:
- Codex selects tender-management based on its description.

## Test 3 — Missing evidence
Provide only a BOQ and request a final price as though all scope were known.

Expected:
- skill identifies missing drawings/specifications/conditions where material;
- does not fabricate scope;
- records assumptions or raises clarifications.

## Test 4 — Skill creator
Invoke `$skill-creator` and request a new rate-analysis skill.

Expected:
- checks existing prompts/skills first;
- defines trigger, inputs, workflow, checks, outputs, QA/QC, and test cases;
- does not create a skill merely by renaming a prompt.

## Acceptance
Foundation passes when Tests 1–4 behave as expected on a real Codex session.
