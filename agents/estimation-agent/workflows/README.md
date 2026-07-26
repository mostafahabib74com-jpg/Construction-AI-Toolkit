# Estimation Agent workflows

Every workflow owns a versioned manifest, input schema, output schema, safety specification, and changelog. The prompt is maintained separately under `../prompts/<workflow-id>/prompt.md`.

A workflow is not production-ready merely because these files exist. It must also have implemented tools, validated calculation services, representative evaluation cases, qualified domain review, and a release approval.

`catalog.yaml` is the authoritative workflow inventory.
