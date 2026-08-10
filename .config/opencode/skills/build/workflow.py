"""The build workflow: a formal specification of the /build converge loop.

This module is valid, runnable Python, but it is not meant to be executed
by the agent. It is a *specification*: the agent reads it and fulfills each
awaited request itself (see SKILL.md). It IS executed by test_workflow.py,
which drives it against mock servers.

Architecture:

- Request: awaitable base class. Awaiting a Request yields it to the driver
  and returns the response sent back via .send().
- Request/Response dataclass pairs: the typed wire format of every operation
  (bash, spawn_subagent, check_alignment, ...).
- Activities: static async methods. Each awaits a Request, unwraps the
  Response, and returns the domain value. Stateless protocol declarations.
- Workflow: instance-based (holds configurable caps). run() is the main
  workflow; align() is the alignment-gate sub-routine.
- Escalate: exception raised to terminate the workflow abnormally.
- drive(): drives a coroutine with a server callable. No event loop
  required -- async/await is loop-agnostic; the .send() protocol that works
  for generators works identically for coroutines.

The plan is ambient: it lives in conversation context, not in this module.
Subjective requests reference the plan implicitly; only computed values
(diffs, subagent outputs) flow through request fields.
"""

import dataclasses
from collections.abc import Callable, Coroutine, Generator
from typing import Any, Literal, TypeVar

T = TypeVar("T")


class Escalate(Exception):
    """Raise to terminate the workflow abnormally, with a reason for the user."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class Request:
    """Base for all request types.

    Awaitable: awaiting a request yields it (self) to the driver and returns
    the response the driver sends back via .send().
    """

    def __await__(self) -> Generator["Request", Any, Any]:
        return (yield self)


@dataclasses.dataclass
class SubagentResult:
    """Domain value returned by Activities.spawn_subagent.

    task_id enables resumption: pass it back to spawn_subagent to continue
    the same subagent session with its context retained.
    """

    task_id: str
    output: str


# ---- Wire types: each operation has a Request/Response pair ----


@dataclasses.dataclass
class BashRequest(Request):
    """Dispatch the bash tool with cmd. Returns BashResponse."""

    cmd: str


@dataclasses.dataclass
class BashResponse:
    stdout: str
    exit_code: int


@dataclasses.dataclass
class SpawnSubagentRequest(Request):
    """Dispatch the task tool. Returns SpawnSubagentResponse.

    task_id=None spawns a fresh session; otherwise the session with that
    task_id is resumed, retaining its context.
    """

    description: str
    prompt: str
    subagent_type: Literal["balanced-subagent", "smart-subagent"]
    task_id: str | None = None


@dataclasses.dataclass
class SpawnSubagentResponse:
    task_id: str
    output: str


@dataclasses.dataclass
class ConstructCoderPromptRequest(Request):
    """Subjective: encode the plan (ambient in conversation context) as a
    coder prompt.

    The prompt must include: the plan as concrete tasks PLUS the intent and
    constraints behind it (the coder has no conversation context -- encode
    the full understanding, not just a task list); the definition of done
    (changes made, tests written, suite passing); and an instruction to run
    the suite before declaring complete.

    Returns ConstructCoderPromptResponse.
    """


@dataclasses.dataclass
class ConstructCoderPromptResponse:
    prompt: str


@dataclasses.dataclass
class CheckAlignmentRequest(Request):
    """Subjective: does diff faithfully implement the plan as agreed in the
    ORIGINAL conversation (not any prompt sent to the coder)?

    Returns CheckAlignmentResponse.
    """

    diff: str


@dataclasses.dataclass
class CheckAlignmentResponse:
    aligned: bool


@dataclasses.dataclass
class GenerateAlignmentFeedbackRequest(Request):
    """Subjective: write feedback correcting the alignment drift in diff.

    Address the specific drift, not the whole plan.

    Returns GenerateAlignmentFeedbackResponse.
    """

    diff: str


@dataclasses.dataclass
class GenerateAlignmentFeedbackResponse:
    feedback: str


@dataclasses.dataclass
class ConstructReviewerPromptRequest(Request):
    """Subjective: construct the reviewer prompt.

    The prompt must instruct the reviewer to: review `git diff`/`git status`;
    find real defects (correctness, edge cases, test gaps, security); write
    adversarial code demonstrating each finding (failing test, repro, PoC);
    and return a numbered findings list (empty == converged).

    Returns ConstructReviewerPromptResponse.
    """


@dataclasses.dataclass
class ConstructReviewerPromptResponse:
    prompt: str


@dataclasses.dataclass
class CheckConvergenceRequest(Request):
    """Subjective: did the reviewer converge (no findings remaining)?

    Interpret reviewer_output against what was asked of the reviewer.

    Returns CheckConvergenceResponse.
    """

    reviewer_output: str


@dataclasses.dataclass
class CheckConvergenceResponse:
    converged: bool


# ---- Activities: side-effecting operations invoked by the workflow ----


class Activities:
    """Protocol declarations for every operation the workflow can perform.

    Each method awaits a Request and returns the unwrapped domain value.
    Methods are stateless; actual fulfillment happens in the driver, which
    routes each awaited request to opencode (production) or a mock server
    (testing). Never instantiate this class.
    """

    @staticmethod
    async def bash(cmd: str) -> str:
        response: BashResponse = await BashRequest(cmd=cmd)
        return response.stdout

    @staticmethod
    async def spawn_subagent(
        description: str,
        prompt: str,
        subagent_type: Literal["balanced-subagent", "smart-subagent"],
        task_id: str | None = None,
    ) -> SubagentResult:
        response: SpawnSubagentResponse = await SpawnSubagentRequest(
            description=description,
            prompt=prompt,
            subagent_type=subagent_type,
            task_id=task_id,
        )
        return SubagentResult(task_id=response.task_id, output=response.output)

    @staticmethod
    async def construct_coder_prompt() -> str:
        response: ConstructCoderPromptResponse = await ConstructCoderPromptRequest()
        return response.prompt

    @staticmethod
    async def check_alignment(diff: str) -> bool:
        response: CheckAlignmentResponse = await CheckAlignmentRequest(diff=diff)
        return response.aligned

    @staticmethod
    async def generate_alignment_feedback(diff: str) -> str:
        response: GenerateAlignmentFeedbackResponse = await GenerateAlignmentFeedbackRequest(
            diff=diff
        )
        return response.feedback

    @staticmethod
    async def construct_reviewer_prompt() -> str:
        response: ConstructReviewerPromptResponse = await ConstructReviewerPromptRequest()
        return response.prompt

    @staticmethod
    async def check_convergence(reviewer_output: str) -> bool:
        response: CheckConvergenceResponse = await CheckConvergenceRequest(
            reviewer_output=reviewer_output
        )
        return response.converged


# ---- Workflow: business logic ----


class Workflow:
    """The build workflow. Parameterized by configurable caps."""

    def __init__(self, max_align_fixes: int = 2, max_review_cycles: int = 3) -> None:
        self.max_align_fixes = max_align_fixes
        self.max_review_cycles = max_review_cycles

    async def run(self) -> str:
        """Run the workflow to convergence.

        Returns the final report. Raises Escalate on abnormal termination.

        The plan is ambient: the agent has it from conversation context.
        Only values computed during the workflow (diffs, subagent outputs)
        are passed through request fields.
        """
        coder_prompt = await Activities.construct_coder_prompt()
        coder = await Activities.spawn_subagent(
            description="implement the agreed plan",
            prompt=coder_prompt,
            subagent_type="balanced-subagent",
        )
        coder_id = coder.task_id

        await self.align(coder_id)

        reviewer_prompt = await Activities.construct_reviewer_prompt()
        reviewer = await Activities.spawn_subagent(
            description="adversarial code review",
            prompt=reviewer_prompt,
            subagent_type="smart-subagent",
        )
        reviewer_id = reviewer.task_id
        converged = await Activities.check_convergence(reviewer.output)

        fixes = 0
        while not converged:
            if fixes >= self.max_review_cycles:
                raise Escalate(f"reviewer did not converge after {self.max_review_cycles} cycles")
            await Activities.spawn_subagent(
                description="apply review findings",
                prompt=reviewer.output,
                subagent_type="balanced-subagent",
                task_id=coder_id,
            )
            await self.align(coder_id)
            reviewer = await Activities.spawn_subagent(
                description="re-review the changes",
                prompt="re-review the current diff",
                subagent_type="smart-subagent",
                task_id=reviewer_id,
            )
            converged = await Activities.check_convergence(reviewer.output)
            fixes += 1

        return f"Converged after {fixes} review cycles."

    async def align(self, coder_id: str) -> None:
        """Alignment gate sub-routine.

        Check the current diff against the original conversation; on drift,
        resume the coder with corrective feedback and re-check. Raises
        Escalate if alignment fails within max_align_fixes attempts.
        """
        fixes = 0
        diff = await Activities.bash("git diff")
        while not (await Activities.check_alignment(diff)):
            if fixes >= self.max_align_fixes:
                raise Escalate("alignment failed; plan or prompt likely ambiguous")
            feedback = await Activities.generate_alignment_feedback(diff)
            await Activities.spawn_subagent(
                description="fix alignment drift",
                prompt=feedback,
                subagent_type="balanced-subagent",
                task_id=coder_id,
            )
            diff = await Activities.bash("git diff")
            fixes += 1


# ---- Driver: routes awaited requests to a server callable ----


def drive(coro: Coroutine[Request, Any, T], server: Callable[[Request], object]) -> T:
    """Drive a coroutine with a server callable (Request -> Response).

    Returns the coroutine's return value, or re-raises any exception it
    raises. No event loop required -- async/await is loop-agnostic; the
    .send() protocol is identical to generator driving.
    """
    try:
        request = coro.send(None)
    except StopIteration as e:
        return e.value
    while True:
        response = server(request)
        try:
            request = coro.send(response)
        except StopIteration as e:
            return e.value
