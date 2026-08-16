from __future__ import annotations

import dataclasses
import enum
from typing import Protocol


@dataclasses.dataclass
class Config:

    max_review_cycles: int = 3


class Workflow:
    """Build-loop: grill, spec, review the spec with the user, then
    autonomously bounce between coder and reviewer until convergence."""

    def __init__(self, agent: Agent, config: Config | None = None) -> None:
        self.agent = agent
        self.config = config or Config()

    async def run(self) -> str:
        await self.agent.reach_shared_understanding()

        spec = await self.agent.write_specification()

        while True:
            feedback = await self.agent.collect_spec_feedback(spec)
            if feedback is None:
                break
            spec = await self.agent.amend_specification(spec, feedback)

        coder = await self.agent.spawn(SubagentType.BALANCED)
        reviewer = await self.agent.spawn(SubagentType.SMART)

        deviations: list[str] = []
        await coder.resume(
            await self.agent.construct_implementation_instructions(spec)
        )

        for cycle in range(1, self.config.max_review_cycles + 1):
            response = await reviewer.resume(
                await self.agent.construct_review_instructions(spec)
            )
            findings = await self.agent.interpret_review(response)
            if findings is None:
                return await self.agent.report_convergence(cycle, deviations)

            spec_flaws = await self.agent.identify_spec_flaws(findings)
            if spec_flaws is not None:
                spec = await self.agent.amend_specification(spec, spec_flaws)
                deviations.append(spec_flaws)

            await coder.resume(
                await self.agent.construct_fix_instructions(findings, spec)
            )

        raise MaxReviewCyclesExceededError


class Subagent(Protocol):

    async def resume(self, prompt: str) -> str:
        """Resume this subagent with new instructions.

        The subagent sees nothing of your conversation; the prompt must
        be self-contained. A subagent that returns no output at all has
        failed to respond — treat that as an error, never as an
        empty-string value.

        Args:
            prompt: The instructions for the subagent.

        Returns:
            The subagent's output text.
        """


class Agent(Protocol):

    async def reach_shared_understanding(self) -> None:
        """Interview the user relentlessly about every aspect of this
        until you reach a shared understanding. Walk down each branch
        of the decision tree, resolving dependencies between decisions
        one-by-one. For each question, provide your recommended answer.

        Ask the questions one at a time, waiting for feedback on each
        question before continuing. Asking multiple questions at once is
        bewildering.

        If a _fact_ can be found by exploring the environment
        (filesystem, tools, etc.), look it up rather than asking the
        user. The _decisions_, though, are the user's — put each one to
        them and wait for their answer.

        Do not move on until the user confirms you have reached a
        shared understanding.
        """

    async def write_specification(self) -> str:
        """Encode the shared understanding and decisions as a text
        specification.

        Do not overspecify; prefer concise and reviewable. Trust the
        implementer to figure out non-essential details.
        """

    async def collect_spec_feedback(self, spec: str) -> str | None:
        """Present the specification to the user and collect their
        feedback.

        Return None once the user approves the specification;
        otherwise return their feedback text.
        """

    async def amend_specification(self, spec: str, feedback: str) -> str:
        """Amend the specification with the given feedback, preserving
        everything already agreed. Return the amended specification.
        """

    async def spawn(self, subagent_type: SubagentType, prompt: str | None = None) -> Subagent:
        """Spawn a new subagent.

        Args:
            subagent_type: The kind of subagent to spawn — FAST for
                simple mechanical work, BALANCED for typical
                development work, SMART for hard or subtle work.
            prompt: Optional setup prompt. If omitted, you must come
                up with a suitable one yourself — introduce the
                subagent's role and tell it that further instructions
                will follow. A subagent sees nothing of your
                conversation, so any prompt you write must be
                self-contained.

        Returns:
            A Subagent handle bound to the spawned session.
        """

    async def construct_implementation_instructions(self, spec: str) -> str:
        """Write the initial instructions for the coder. They must be
        self-contained (the coder sees nothing else): include the full
        specification and instruct the coder to implement it and report
        when done.
        """

    async def construct_review_instructions(self, spec: str) -> str:
        """Write instructions for the reviewer.

        They must be self-contained: instruct the reviewer to inspect
        the repository state (e.g. git diff, git status) against the
        full specification included in the instructions, find real
        defects (correctness, edge cases, test gaps, security),
        demonstrate each finding with adversarial code (failing test,
        repro, PoC), and reply with a numbered findings list — or, when
        no defects were found, state that verdict explicitly. For
        follow-up reviews, adapt to what was previously reported.
        """

    async def interpret_review(self, response: str) -> str | None:
        """Interpret the reviewer's reply.

        Return the findings as text if the reviewer reports defects;
        return None if the reviewer reports no defects. If the reply is
        empty or too ambiguous to classify, raise
        ReviewerProtocolError.
        """

    async def identify_spec_flaws(self, findings: str) -> str | None:
        """Examine the reviewer's findings and identify those that stem
        from flaws in the specification itself rather than
        implementation defects.

        Return them as text, or None if every finding is an
        implementation defect.
        """

    async def construct_fix_instructions(self, findings: str, spec: str) -> str:
        """Write instructions for the coder addressing the reviewer's
        findings. Specification flaws, if any, have already been
        amended into the spec passed here.

        The instructions must be self-contained: address the specific
        findings (not the whole spec), include the full current
        specification, and instruct the coder to fix and report.
        """

    async def report_convergence(self, cycle: int, deviations: list[str]) -> str:
        """Compose the final report: the implementation converged after
        the given number of review cycles, listing any deviations from
        the specification that were made along the way.
        """


class SubagentType(enum.Enum):

    FAST = "fast"
    BALANCED = "balanced"
    SMART = "smart"


class ReviewerProtocolError(Exception):
    """The reviewer's reply could not be interpreted as a verdict.
    When surfacing this abort, include the raw reply verbatim."""


class MaxReviewCyclesExceededError(Exception):
    """The implementation did not converge within the configured
    number of review cycles. When surfacing this abort: explain how
    many cycles were attempted, summarize the reviewer's last
    findings, and note that the coder already applied fixes for them
    which were never re-reviewed — suggest the user request one more
    review."""
