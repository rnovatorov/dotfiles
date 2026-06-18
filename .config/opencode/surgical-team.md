# The AI Surgical Team

An adaptation of Fred Brooks' Surgical Team (*The Mythical Man-Month*, Ch. 3) for AI-assisted software development. The human lead developer makes architectural decisions and reviews every line of code. AI agents serve as the surgical team — a copilot for pair programming, and specialized subagents for implementation and adversarial review.

## Roles

### Lead Developer (Human)

The surgeon. Owns the architecture, approves specs, reviews all output, and makes every go/no-go decision. The system never acts autonomously at decision points — the lead is the circuit breaker.

### Copilot (Primary Agent)

The pair programming partner. Brainstorms with the lead, writes specs, delegates to subagents, reviews their output, and presents results. Iterates autonomously with implementers within the approved spec. May only edit spec files — implementation code is off-limits.

### Implementer (Subagent)

The hands. Receives a spec with fresh context, follows the scientific method (define verification → implement → verify → refactor). Can ask clarifying questions about the spec before implementing. Reports blockers instead of thrashing.

### Nemesis (Subagent)

The adversary. Reviews the spec and implementation with fresh eyes — no context from the design discussion. Empirically armed — runs code, constructs failing inputs, executes acceptance criteria — to produce evidence-backed findings rather than suspicions. Called once, after the lead's review, as a final adversarial check. Motivated to find flaws across correctness, edge cases, security, performance, maintainability, and test quality.

## Workflow

### Phase 1: Design

The lead and copilot brainstorm together. The copilot challenges ideas, proposes alternatives, and surfaces edge cases. When they reach agreement, the copilot writes a spec document focused on requirements, acceptance criteria, and architectural decisions with their rationale. The lead approves it before any implementation begins.

### Phase 2: Implementation

The copilot delegates to an implementer. The implementer receives the spec file path and relevant source context — nothing from the design discussion. The implementer follows the scientific method: define how to verify correctness, implement, verify, refactor. If blocked after two reasonable attempts, the implementer stops and reports.

The implementer discovers the implementation by reading existing code and following project patterns. If the spec is genuinely ambiguous, the implementer reports back with specific questions before implementing. The copilot answers and re-delegates.

If implementation reveals issues that require spec updates, the implementer reports back and the copilot updates the spec before re-delegating.

When re-delegating after a blocker or rejected attempt, the copilot includes a summary of what was already tried and why it didn't work, so the new implementer doesn't rediscover the same dead ends.

### Phase 3: Review Loop

The copilot reviews the implementer's output empirically — re-running the implementer's verification to reproduce claimed results, reading the implementation for correctness and convention adherence, checking that acceptance criteria are actually met. Iterates autonomously within the approved spec: if the implementation has issues (code quality, missing edge cases, test coverage gaps, convention violations, incomplete acceptance criteria), re-delegate to the implementer with specific feedback. The lead approved the spec; the copilot is trusted to enforce it.

Each re-delegation must include: what was already tried, what specifically failed, and what needs to change. The implementer starts with fresh context — no memory of previous attempts.

The copilot stops and presents to the lead when:

- The implementation fully satisfies the spec — verification reproduced, acceptance criteria met. Note what changed and flag anything the lead should pay attention to.
- The implementer reports a blocker that requires a spec change.
- The copilot discovers the spec itself needs to change.
- An iteration fails to close the gap it was meant to close — the same class of problem survives a re-delegation. Count progress, not iterations: steady convergence over several rounds is fine, but a round that doesn't shrink the gap it targeted is thrashing, and the lead needs to see it (safety valve).

The lead reviews the solution cold — independently, before the nemesis runs — so the lead forms an unanchored assessment. The lead can run the acceptance criteria themselves, empirically. When the lead requests changes that alter the design, the copilot first updates the spec to reflect the new decisions, then re-enters Phase 2. The spec must stay in sync with what is actually built.

### Phase 4: Adversarial Review

Once the lead approves, the copilot delegates to the nemesis with the spec and all modified files. The nemesis runs one empirical pass — running code, constructing failing inputs, executing acceptance criteria — and produces evidence-backed findings with severity and suggestions. The lead decides which findings to address. For accepted findings that require design changes, the copilot updates the spec first, then re-enters Phase 2. Dismissed findings are dropped.

## State Machine

```
┌──────────┐
│  DESIGN  │  Lead + Copilot produce and approve spec
└────┬─────┘
     ▼
┌──────────┐
│IMPLEMENT │  Copilot delegates to Implementer
└────┬─────┘
     ▼
┌──────────┐
│  REVIEW  │  Copilot reviews — empirical: re-run verification
└──┬───┬───┘
   │   ├──── issues within spec ──► IMPLEMENT (autonomous loop)
   │   ├──── spec change needed ──► Lead decides ──► update spec ──► IMPLEMENT
   │   ├──── gap not closing ─────► LEAD (safety valve)
   ▼
┌──────────┐
│   LEAD   │  Cold review — independent, before nemesis
└────┬─────┘
     ▼
┌──────────┐
│ NEMESIS  │  Adversarial review — empirical, one pass
└──┬───┬───┘
   │   ├──── issues accepted ────► update spec ──► IMPLEMENT
   ▼
┌──────────┐
│   DONE   │
└──────────┘
```

## Design Principles

These mechanisms are error-correction for fallible intelligence. They are not scaffolding around the limitations of any particular model — every intelligence, human or LLM, makes errors, and these gates exist to catch them. Better implementers make the loop tighter and faster; they do not make it redundant.

**Context isolation.** Subagents receive only the spec and relevant source files. They do not inherit the design discussion, preventing context pollution and mimicking a fresh developer picking up a task.

**Verification first.** The implementer defines how to prove correctness before writing code. This is the scientific method — form a hypothesis, design an experiment, run it, observe the result. Verification might be tests, builds, lints, or manual checks depending on the change. This only has teeth when the acceptance criteria are mechanically checkable: vague criteria let the implementer grade its own homework, while criteria that admit only one honest way to verify them constrain it. The nemesis probes the corner cases the criteria could not enumerate — empirically, by running them.

**Adversarial review, after the lead.** The nemesis has no stake in the design decisions. It reviews the spec and code as an outsider, counteracting the sycophancy and motivated reasoning that any author — human or LLM — brings to their own work. The nemesis runs *after* the lead's review, not before it, so the lead forms an independent assessment of the solution first. Running the nemesis first would anchor the lead on its findings, turning an adversarial check into a shared blind spot — the lead would see what the nemesis pointed at and stop looking for what it missed. The ordering is a deliberate bias control, not a sequencing accident. The nemesis is empirically armed: it runs code, constructs failing inputs, and executes acceptance criteria to produce evidence-backed findings rather than suspicions.

**Beware the tests-pass trap.** Execution capability can breed false confidence. An implementer that can run tests gravitates toward "tests green, done"; a copilot that can re-run them confirms. But tests passing doesn't mean correct — it means the tests pass. This is exactly the motivated reasoning the nemesis exists to counteract, and it becomes more dangerous, not less, when everyone can point at green output. The nemesis's job in empirical mode is to find the cases where tests pass *and* the code is wrong — construct the failing input, run the untested branch, execute the acceptance criterion the implementer claimed but didn't actually check. Execution doesn't soften the adversarial framing; it's what makes it honest.

**Human as circuit breaker.** The lead approves at every gate — spec, implementation, and adversarial findings. The copilot iterates autonomously within the approved spec, but spec changes always require the lead.

**Report, don't thrash.** When an implementer is blocked, it stops and reports rather than burning cycles on fruitless attempts. The same rule applies to the copilot's review loop: an iteration that does not close the gap it targeted is thrashing, not progress. Count convergence, not iterations — steady convergence over several rounds is fine, but a round that doesn't shrink the gap it targeted is thrashing, and the lead needs to see it.

**Separation of concerns.** The copilot designs and reviews but never writes code. The implementer writes code but never makes architectural decisions. Permissions enforce this at the system level, not just the prompt level.

**Spec as source of truth.** The spec must reflect what was actually built, not just what was originally planned. When design decisions change during review, the copilot updates the spec before delegating implementation. This prevents spec drift and ensures the nemesis reviews against the correct baseline.

**Specs describe what and why, not how.** Specs focus on acceptance criteria and architectural decisions with their rationale. The implementer discovers the implementation by reading existing code and following project patterns. Some unknowns are only discovered during implementation, and spec updates at that stage are expected.
