---
name: commit-messages
description: Enforce structured commit message format. Use when creating git commits or writing commit messages.
---

# Writing Commit Messages

## Overview

Every commit message follows a consistent format. The subject line completes
the sentence: **"If applied, this commit will _\<your subject line\>_"**. When
present, the body explains **why**, not what.

## Detect Project Convention First

Follow existing instructions for commits if present in the repository. Check
`git log --oneline -20` to see recent patterns and match the existing style.

**Project convention always wins.** The rules below are the default when no
convention is detected.

## References

Consider the following references when creating new commit messages:

- **Subject line rules, body format, URLs, issue references**:
  [references/commit_format.md](references/commit_format.md)
- **Split strategies, anti-rationalizations, and refactoring patterns**:
  [references/atomic_commits.md](references/atomic_commits.md)
