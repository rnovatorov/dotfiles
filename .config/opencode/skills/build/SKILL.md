---
name: build
description: Implement an agreed plan via a coder + reviewer subagent converge loop with an alignment gate. Use when asked to build or implement a plan already agreed on in this conversation.
---

# Build

Orchestrate a coder subagent, an alignment gate, and a reviewer subagent in a
converge loop. The workflow is specified as real Python in
[workflow.py](workflow.py) in this directory -- read it first, then trace
`Workflow().run()` as if you were its driver.

The plan is **ambient**: it lives in this conversation's context, not in any
parameter. Subjective requests reference it implicitly; only computed values
(diffs, subagent outputs) flow through request fields.

**Interpret, do not execute.** Never run `python workflow.py` -- the
activities have no real implementation; awaiting one yields a request for
YOU to fulfill. (The module is runnable for testing: test_workflow.py drives
it against mock servers. Execution is not your job -- interpretation is.)

For each `await Activities.<method>(...)`, find the Request type it awaits;
its docstring states the contract and the Response type. Fulfill it:

- **Tool requests** (`BashRequest`, `SpawnSubagentRequest`): dispatch the
  matching opencode tool (`bash`, `task`) with the request's fields.
- **Subjective requests** (`ConstructCoderPromptRequest`,
  `CheckAlignmentRequest`, `GenerateAlignmentFeedbackRequest`,
  `ConstructReviewerPromptRequest`, `CheckConvergenceRequest`): apply your
  judgment against this conversation, the source of truth.

Then continue the trace with the activity returning your response's
unwrapped value.

- Track workflow variables (`coder_id`, `reviewer_id`, `diff`, `fixes`, ...)
  in memory across turns; resuming a subagent means passing its saved
  `task_id` back to the `task` tool.
- On `Escalate`: stop immediately and surface the reason to the user.
- On normal return: surface the returned string as the final report.
