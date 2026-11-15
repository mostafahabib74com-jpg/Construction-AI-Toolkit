# Cross-agent artifact control

- Record artifact ID, owning agent, workflow, version, status, checksum, approval role, and approval time.
- Use only approved or explicitly conditionally approved artifacts in final proposal assembly.
- Preserve calculations and facts from the owning artifact; do not silently retype, recalculate, round, reinterpret, or optimize them.
- When proposal formatting requires aggregation, use deterministic transformations and reconcile to the source totals.
- If two artifacts conflict, open a reconciliation action with both owners and block the affected conclusion.
- A new upstream version makes the downstream section stale until impact review and reapproval are complete.
