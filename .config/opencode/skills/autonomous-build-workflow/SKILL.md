---
name: autonomous-build-workflow
description: Use when asked to run autonomous-build-workflow or when the user wants something built collaboratively — grill the user for shared understanding, write a specification, review it together, then autonomously bounce between a coder and a reviewer subagent until the implementation converges.
---

# Autonomous Build Workflow

A workflow that turns a rough idea into a converged implementation:

1. Interviews the user relentlessly until a shared understanding is
   reached.
2. Writes a concise text specification and reviews it with the user
   in a feedback loop until approved.
3. Runs autonomously: a coder implements, a reviewer hunts real
   defects with adversarial code, and the orchestrator relays findings
   back to the coder — amending the spec itself when a finding stems
   from a spec flaw, recording each such deviation.
4. Reports convergence with any deviations, or aborts after
   `Config.max_review_cycles` (default 3).

This is a workflow. Load the `workflows` skill first, then read and
carry out `workflow.py` in this directory following its rules.
