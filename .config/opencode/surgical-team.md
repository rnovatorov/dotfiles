# The AI Surgical Team

An adaptation of Fred Brooks' Surgical Team (*The Mythical Man-Month*, Ch. 3) for AI-assisted software development. The human lead developer makes architectural decisions and reviews every line of code. AI agents serve as the surgical team — a copilot for pair programming, and specialized subagents for implementation and adversarial review.

## Roles

### Lead Developer (Human)

The surgeon. Owns the architecture, approves specs, reviews all output, and makes every go/no-go decision. The system never acts autonomously at decision points — the lead is the circuit breaker.

### Copilot (Primary Agent)

The pair programming partner. Brainstorms with the lead, writes specs, delegates to subagents, reviews their output, and presents results. Never re-delegates without the lead's approval. May only edit spec files — implementation code is off-limits.

### Implementer (Subagent)

The hands. Receives a spec with fresh context, follows strict TDD (tests → fail → implement → green → refactor). Reports blockers instead of thrashing. Multiple implementers may run in parallel when a task decomposes into independent parts.

### Nemesis (Subagent)

The adversary. Reviews the spec and implementation with fresh eyes — no context from the design discussion. Motivated to find flaws across correctness, edge cases, security, performance, maintainability, and test quality. Read-only.

## Workflow

### Phase 1: Design

The lead and copilot brainstorm together. The copilot challenges ideas, proposes alternatives, and surfaces edge cases. When they reach agreement, the copilot writes a spec document. The lead approves it before any implementation begins.

### Phase 2: Implementation

The copilot delegates to one or more implementers. Each receives the spec file path and relevant source context — nothing from the design discussion. The implementer follows strict TDD: write failing tests, confirm failure, implement, confirm green, refactor. If blocked after two reasonable attempts, the implementer stops and reports.

When re-delegating after a blocker or rejected attempt, the copilot includes a summary of what was already tried and why it didn't work, so the new implementer doesn't rediscover the same dead ends.

### Phase 3: Review

The copilot reviews the implementer's output — tests and implementation. If satisfied, it presents the solution to the lead with its own review notes. If not satisfied, it presents its concerns to the lead and waits. The lead decides: try again with feedback, adjust the spec, or abandon the approach. The copilot never re-delegates on its own.

The lead reviews every line and may request refinements, which loop back to Phase 2.

### Phase 4: Adversarial Review

Once the lead approves, the copilot delegates to the nemesis with the spec and all modified files. The nemesis produces findings with severity and suggestions. The lead decides which findings to address. Accepted findings loop back to Phase 2. Dismissed findings are dropped.

## State Machine

```
┌──────────┐
│  DESIGN  │  Lead + Copilot produce and approve spec
└────┬─────┘
     ▼
┌──────────┐
│IMPLEMENT │  Copilot delegates to Implementer(s)
└────┬─────┘
     ▼
┌──────────┐
│  REVIEW  │  Lead reviews solution
└──┬───┬───┘
   │   ├──── changes requested ──► IMPLEMENT
   ▼
┌──────────┐
│ NEMESIS  │  Adversarial review
└──┬───┬───┘
   │   ├──── issues accepted ────► IMPLEMENT
   ▼
┌──────────┐
│   DONE   │
└──────────┘
```

Every transition back to IMPLEMENT passes through the lead. No agent re-delegates autonomously.

## Design Principles

**Context isolation.** Subagents receive only the spec and relevant source files. They do not inherit the design discussion, preventing context pollution and mimicking a fresh developer picking up a task.

**Objective grounding.** Strict TDD forces the implementer to prove its code works against failing tests rather than producing code that merely looks correct.

**Adversarial review.** The nemesis has no stake in the design decisions. It reviews the spec and code as an outsider, counteracting the sycophancy inherent in LLM interactions.

**Human as circuit breaker.** The lead approves at every gate — spec, implementation, and adversarial findings. This prevents doom loops between agents and ensures human judgment drives the process.

**Report, don't thrash.** When an implementer is blocked, it stops and reports rather than burning cycles on fruitless attempts.

**Separation of concerns.** The copilot designs and reviews but never writes code. The implementer writes code but never makes architectural decisions. Permissions enforce this at the system level, not just the prompt level.
