---
name: workflows
description: Use when asked to execute or write a workflow. Workflows are formal Python specifications the agent carries out action by action.
---

# Workflows

A workflow is a formal specification of agent behavior, written as
async/await Python in a single self-contained file.

Workflows are **never executed as scripts**. Do not run
`python workflow.py`. Instead, you read the file and carry it out:
you perform the actions it prescribes yourself, following the control
flow written in the code.

## Anatomy

A workflow file has four parts.

### `Workflow` — the control flow

The `Workflow` class is the program. Its `__init__` takes an
`agent: Agent` plus optional configuration (plain keyword arguments
with defaults, or a `Config` dataclass) and stores it. Its
`async def run()` method contains the control flow: loops,
conditionals, and the actions that define the workflow.

### `Agent` — the actions

`Agent` is a `typing.Protocol` describing the capabilities the workflow
relies on. Each method prescribes one action:

- The **signature** declares the action's inputs and the type of value
  it returns.
- The **docstring** is the prompt: instructions for what to do.

Protocol method bodies contain **only the docstring** — no `...`, no
`raise NotImplementedError()`. The docstring is the body.

Two kinds of methods commonly appear:

- **Primitives** shared across workflows, such as `spawn` (start a
  subagent).
- **Domain methods** unique to each workflow. Their docstrings
  describe an outcome. Achieve it however is appropriate, then return
  a value of the annotated type.

### `Subagent` — a running subagent session

A handle returned by `spawn`, bound to one subagent session. `spawn`
takes a `SubagentType` — an enum of the kinds of subagent available —
and an optional setup prompt; when the prompt is omitted, you must
write a self-contained one yourself, introducing the subagent's role
and telling it that further instructions will follow. The handle's
single method, `resume(prompt)`, continues that session with new
instructions. A subagent sees nothing of your conversation — every
prompt sent to one must be self-contained. A subagent that returns
no output at all has failed to respond — treat that as an error,
never as an empty-string value.

### Supporting types

Dataclasses, enums, and custom exceptions define the types referenced
by the signatures.

## Executing a workflow

1. **Read the entire file before starting.** Carry out only a
   workflow you have read in full.
2. **You are the agent.** The `Workflow` class is the program; you are
   the `Agent` implementation it runs against. Begin at
   `Workflow.run()` and follow the code.
3. **Evaluate the Python yourself.** Tracking variables, iterating
   loops, testing conditionals — that is all work you do, no less than
   the awaits. Every `await` of an `Agent` method or of
   `Subagent.resume` is an action you must actually perform: read the
   method's docstring, do what it says, and continue with a value of
   the annotated type.
4. **Sequential awaits run in order.** Complete one action fully
   before starting the next.
5. **`asyncio.gather(...)` runs its calls concurrently.** Perform all
   of those actions, then continue with the collected results.
6. **On exception, stop.** If an action raises — a workflow-defined
   error or an unhandled failure — stop and surface the exception to
   the user. A workflow-defined error is raised with an empty
   message; its class docstring says what context to surface. Do not
   improvise recovery the workflow does not specify.
7. **On normal return, report.** When `run()` returns, surface the
   returned value to the user as the final report.

Follow the code faithfully. It is the source of truth for what happens
and in what order — never skip, reorder, or invent actions. When a
docstring leaves room for judgment, use it, but stay within its stated
purpose.

## Writing a new workflow

Study `references/build-and-review/` in this skill directory — it
shows the conventions. Then write the file:

1. Fill in the `Workflow` class: a class docstring, configuration
   in `__init__`, and the control flow in `run()`. Artifacts the
   workflow works on are not configuration — obtain them at runtime
   through `Agent` methods.
2. Add methods to the `Agent` protocol. Give each a precise typed
   signature and a docstring that fully instructs the executing agent.
   The docstring is all the guidance that agent gets, so make it
   self-contained: context, rules, and expected output.
3. Define any dataclasses, enums, or exceptions referenced by the
   signatures.

Keep `run()` free of prose: no prompt strings inline — build prompts
in domain methods, so the executing agent can shape them. Return
whatever value the control flow naturally produces.
Abort by raising a workflow-defined exception with an empty message,
and put the instructions for what to surface in the exception's class
docstring.

Optionally, add `test_workflow.py` beside the workflow: implement a
fake `Agent` and call `asyncio.run(Workflow(agent).run())` to verify
the control flow. Tests really do execute the code — that is fine for
tests. It is only the executing agent that never runs the file.
