---
name: scientific-method
description: Acquire knowledge empirically. Use for testing, debugging and root cause analysis.
---

# Scientific Method

A reliable way of acquiring knowledge through careful observation, rigorous
skepticism, hypothesis testing, and experimental validation.

## Observation

Whenever you notice something that catches your attention, ask yourself: _why_
is this the way it is?

Example:

> Observation: A regex worked correctly on a few manual test inputs.

## Hypothesis

Form a hypothesis which could explain the observation. Good hypotheses can be
proven wrong and therefore have predictive power. Falsifiability is a _must_.
Prefer the simplest hypothesis consistent with what you've observed so far.

Example:

> Hypothesis: The regex handles all inputs correctly.

## Experiment

Design an experiment that could disprove your hypothesis, not just confirm it.
Change one variable at a time - if you alter several things at once and the
result shifts, you won't know which change mattered.

Depending on what you have access to, this might mean:

- **Running code** - write a minimal reproduction, isolate the suspected
  variable, and execute it
- **Searching** - check whether others have documented the same behavior, or
  whether a library's known issues match your hypothesis
- **Reading existing data/logs** - before running anything new, check if the
  evidence to confirm or disprove the hypothesis already exists
- **Asking the user** - for anything you can't observe or run directly, ask for
  the specific evidence you need instead of guessing

Evidence contradicts the hypothesis? Well done - that's a real result. Form a
new hypothesis and repeat.

Evidence supports it? It _might_ be the explanation. No guarantees - only
increased confidence. Watch for confounders: did anything else change between
runs besides the variable you meant to isolate?

Example:

> Experiment: Check an edge case. A single failing input is found -> the
> hypothesis is disproven, no matter how many inputs passed before.

Another example:

> Experiment: Check an edge case. All inputs pass -> supports the hypothesis,
> but never proves it.

## Limits of Knowledge

There are things we don't fully understand. If you've formed and tested several
reasonable hypotheses and still have no answer, accept it and say so plainly
rather than presenting a guess as a conclusion.
