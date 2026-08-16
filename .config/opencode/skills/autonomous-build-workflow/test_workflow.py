import asyncio

import pytest

from workflow import (
    MaxReviewCyclesExceededError,
    ReviewerProtocolError,
    SubagentType,
    Workflow,
)


def clamped(sequence, index):
    return sequence[min(index, len(sequence) - 1)]


class FakeSubagent:
    def __init__(self, responses):
        self.responses = list(responses)
        self.resumes = []

    async def resume(self, prompt: str) -> str:
        self.resumes.append(prompt)
        return clamped(self.responses, len(self.resumes) - 1)


class FakeAgent:
    def __init__(self, *, feedback_sequence=(None,), findings_sequence=("",), flaws_sequence=(None,)):
        self.feedback_sequence = list(feedback_sequence)
        self.findings_sequence = list(findings_sequence)
        self.flaws_sequence = list(flaws_sequence)
        self.spawns = []
        self.amendments = []
        self.flaw_inspections = 0
        self.grilled = False

    async def reach_shared_understanding(self):
        self.grilled = True

    async def write_specification(self):
        return "spec v1"

    async def collect_spec_feedback(self, spec):
        return clamped(self.feedback_sequence, len(self.amendments))

    async def amend_specification(self, spec, feedback):
        self.amendments.append(feedback)
        return f"{spec} + amended({feedback})"

    async def spawn(self, subagent_type, prompt=None):
        if subagent_type == SubagentType.SMART:
            subagent = FakeSubagent(self.findings_sequence)
        else:
            subagent = FakeSubagent(["ok"])
        self.spawns.append((subagent_type, subagent))
        return subagent

    async def construct_implementation_instructions(self, spec):
        return f"implement: {spec}"

    async def construct_review_instructions(self, spec):
        return f"review against: {spec}"

    async def identify_spec_flaws(self, findings):
        flaws = clamped(self.flaws_sequence, self.flaw_inspections)
        self.flaw_inspections += 1
        return flaws

    async def construct_fix_instructions(self, findings, spec):
        return f"fix: {findings}; spec: {spec}"

    async def interpret_review(self, response):
        if "no defects" in response:
            return None
        return response

    async def report_convergence(self, cycle, deviations):
        return f"report: converged in {cycle}; deviations: {deviations}"


def test_spec_review_loop_with_human_feedback():
    agent = FakeAgent(
        feedback_sequence=("tighten scope", "add rollback", None),
        findings_sequence=("no defects found",),
    )
    result = asyncio.run(Workflow(agent).run())

    # Feedback rounds drive amendments until approval.
    assert agent.amendments == ["tighten scope", "add rollback"]
    _, coder = agent.spawns[0]
    _, reviewer = agent.spawns[1]

    # The built spec incorporates both amendments, in order.
    assert coder.resumes[0] == "implement: spec v1 + amended(tighten scope) + amended(add rollback)"
    assert reviewer.resumes[0].endswith("add rollback)")

    assert result == "report: converged in 1; deviations: []"


def test_spec_flaw_amendment_records_deviation():
    agent = FakeAgent(
        findings_sequence=("1. errors mishandled", "no defects found"),
        flaws_sequence=("spec gap: error handling unspecified", None),
    )
    result = asyncio.run(Workflow(agent).run())

    _, coder = agent.spawns[0]
    _, reviewer = agent.spawns[1]

    # The flaw was amended into the spec mid-build and recorded as a deviation.
    assert agent.amendments == ["spec gap: error handling unspecified"]
    assert "amended(spec gap" in reviewer.resumes[1]
    assert "amended(spec gap" in coder.resumes[1]

    assert result == "report: converged in 2; deviations: ['spec gap: error handling unspecified']"


def test_nonconvergence_aborts():
    agent = FakeAgent(
        findings_sequence=("1. broken",) * 3,
    )

    with pytest.raises(MaxReviewCyclesExceededError):
        asyncio.run(Workflow(agent).run())

    _, coder = agent.spawns[0]
    _, reviewer = agent.spawns[1]
    assert len(reviewer.resumes) == 3
    assert len(coder.resumes) == 4


def test_uninterpretable_reply_stops_the_workflow():
    class AmbiguousAgent(FakeAgent):
        async def interpret_review(self, response):
            raise ReviewerProtocolError

    agent = AmbiguousAgent(findings_sequence=("hmm",))

    with pytest.raises(ReviewerProtocolError):
        asyncio.run(Workflow(agent).run())

    # No fix round happened: the coder was resumed only for the
    # initial implementation.
    _, coder = agent.spawns[0]
    assert len(coder.resumes) == 1
