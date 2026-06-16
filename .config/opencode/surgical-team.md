# The AI Surgical Team

An adaptation of Fred Brooks' Surgical Team (*The Mythical Man-Month*, Ch. 3) for AI-assisted software development. The human lead developer makes architectural decisions and reviews every line of code. AI agents serve as the surgical team — a copilot for pair programming, and specialized subagents for implementation and adversarial review.

## Roles

### Lead Developer (Human)

The surgeon. Owns the architecture, approves specs, reviews all output, and makes every go/no-go decision. The system never acts autonomously at decision points — the lead is the circuit breaker.

### Copilot (Primary Agent)

The pair programming partner. Brainstorms with the lead, writes specs, delegates to subagents, reviews their output, and presents results. Iterates autonomously with implementers within the approved spec. May only edit spec files — implementation code is off-limits.

### Implementer (Subagent)

The hands. Receives a spec with fresh context, follows the scientific method (define verification → implement → verify → refactor). Can ask clarifying questions about the spec before implementing. Reports blockers instead of thrashing. Multiple implementers may run in parallel when a task decomposes into independent parts.

### Nemesis (Subagent)

The adversary. Reviews the spec and implementation with fresh eyes — no context from the design discussion. Motivated to find flaws across correctness, edge cases, security, performance, maintainability, and test quality. Read-only.

## Workflow

### Phase 1: Design

The lead and copilot brainstorm together. The copilot challenges ideas, proposes alternatives, and surfaces edge cases. When they reach agreement, the copilot writes a spec document focused on requirements, acceptance criteria, and architectural decisions with their rationale. The lead approves it before any implementation begins.

### Phase 2: Implementation

The copilot delegates to one or more implementers. Each receives the spec file path and relevant source context — nothing from the design discussion. The implementer follows the scientific method: define how to verify correctness, implement, verify, refactor. If blocked after two reasonable attempts, the implementer stops and reports.

The implementer discovers the implementation by reading existing code and following project patterns. If the spec is genuinely ambiguous, the implementer reports back with specific questions before implementing. The copilot answers and re-delegates.

If implementation reveals issues that require spec updates, the implementer reports back and the copilot updates the spec before re-delegating.

When re-delegating after a blocker or rejected attempt, the copilot includes a summary of what was already tried and why it didn't work, so the new implementer doesn't rediscover the same dead ends.

### Phase 3: Review Loop

The copilot reviews the implementer's output — tests and implementation — and iterates autonomously. If the implementation has issues within the spec (code quality, missing edge cases, test coverage gaps, convention violations), the copilot re-delegates with specific feedback. The lead approved the spec; the copilot is trusted to enforce it.

The copilot stops and presents to the lead when:

- The implementation fully satisfies the spec
- The implementer reports a blocker that requires a spec change
- The copilot discovers the spec itself needs to change
- The copilot has iterated three times without convergence (safety valve)

The lead reviews every line and may request refinements. When the lead requests changes that alter the design, the copilot first updates the spec to reflect the new decisions, then delegates the implementation changes. The spec must stay in sync with what is actually built.

### Phase 4: Adversarial Review

Once the lead approves, the copilot delegates to the nemesis with the spec and all modified files. The nemesis produces findings with severity and suggestions. The lead decides which findings to address. For accepted findings that require design changes, the copilot updates the spec first, then delegates implementation. Dismissed findings are dropped.

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
│  REVIEW  │  Copilot reviews implementation
└──┬───┬───┘
   │   ├──── issues within spec ──► IMPLEMENT (autonomous loop)
   │   ├──── spec change needed ──► Lead decides ──► update spec ──► IMPLEMENT
   ▼
┌──────────┐
│   LEAD   │  Lead reviews final solution
└────┬─────┘
     ▼
┌──────────┐
│ NEMESIS  │  Adversarial review
└──┬───┬───┘
   │   ├──── issues accepted ────► update spec ──► IMPLEMENT
   ▼
┌──────────┐
│   DONE   │
└──────────┘
```

## Design Principles

**Context isolation.** Subagents receive only the spec and relevant source files. They do not inherit the design discussion, preventing context pollution and mimicking a fresh developer picking up a task.

**Verification first.** The implementer defines how to prove correctness before writing code. This is the scientific method — form a hypothesis, design an experiment, run it, observe the result. Verification might be tests, builds, lints, or manual checks depending on the change.

**Adversarial review.** The nemesis has no stake in the design decisions. It reviews the spec and code as an outsider, counteracting the sycophancy inherent in LLM interactions.

**Human as circuit breaker.** The lead approves at every gate — spec, implementation, and adversarial findings. The copilot iterates autonomously within the approved spec, but spec changes always require the lead.

**Report, don't thrash.** When an implementer is blocked, it stops and reports rather than burning cycles on fruitless attempts.

**Separation of concerns.** The copilot designs and reviews but never writes code. The implementer writes code but never makes architectural decisions. Permissions enforce this at the system level, not just the prompt level.

**Spec as source of truth.** The spec must reflect what was actually built, not just what was originally planned. When design decisions change during review, the copilot updates the spec before delegating implementation. This prevents spec drift and ensures the nemesis reviews against the correct baseline.

**Specs describe what and why, not how.** Specs focus on acceptance criteria and architectural decisions with their rationale. The implementer discovers the implementation by reading existing code and following project patterns. Some unknowns are only discovered during implementation, and spec updates at that stage are expected.
