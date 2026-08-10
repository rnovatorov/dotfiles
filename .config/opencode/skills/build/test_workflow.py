"""Tests for the build workflow control flow.

Each test drives Workflow().run() with a local mock server callable that
fulfills each Request type with canned responses, via drive().
"""

import pytest

from workflow import (
    BashRequest,
    BashResponse,
    CheckAlignmentRequest,
    CheckAlignmentResponse,
    CheckConvergenceRequest,
    CheckConvergenceResponse,
    ConstructCoderPromptRequest,
    ConstructCoderPromptResponse,
    ConstructReviewerPromptRequest,
    ConstructReviewerPromptResponse,
    Escalate,
    GenerateAlignmentFeedbackRequest,
    GenerateAlignmentFeedbackResponse,
    SpawnSubagentRequest,
    SpawnSubagentResponse,
    Workflow,
    drive,
)


def test_happy_path():
    """Everything succeeds on the first try; converges immediately."""
    log = []

    def server(request):
        log.append(request)
        if isinstance(request, ConstructCoderPromptRequest):
            return ConstructCoderPromptResponse(prompt="coder prompt")
        if isinstance(request, SpawnSubagentRequest):
            task_id = "coder-1" if request.subagent_type == "balanced-subagent" else "reviewer-1"
            return SpawnSubagentResponse(task_id=task_id, output="subagent output")
        if isinstance(request, BashRequest):
            return BashResponse(stdout="diff content", exit_code=0)
        if isinstance(request, CheckAlignmentRequest):
            return CheckAlignmentResponse(aligned=True)
        if isinstance(request, ConstructReviewerPromptRequest):
            return ConstructReviewerPromptResponse(prompt="reviewer prompt")
        if isinstance(request, CheckConvergenceRequest):
            return CheckConvergenceResponse(converged=True)
        if isinstance(request, GenerateAlignmentFeedbackRequest):
            return GenerateAlignmentFeedbackResponse(feedback="fix it")
        raise ValueError(f"unhandled request: {request}")

    report = drive(Workflow().run(), server)

    assert report == "Converged after 0 review cycles."
    spawns = [r for r in log if isinstance(r, SpawnSubagentRequest)]
    assert [s.subagent_type for s in spawns] == ["balanced-subagent", "smart-subagent"]
    assert all(s.task_id is None for s in spawns)  # both spawned fresh
    # alignment passed first try: no feedback was ever generated
    assert not any(isinstance(r, GenerateAlignmentFeedbackRequest) for r in log)


def test_alignment_drift_recovery():
    """Alignment fails on the first check, succeeds after one fix."""
    alignment_checks = 0
    spawns = []

    def server(request):
        nonlocal alignment_checks
        if isinstance(request, ConstructCoderPromptRequest):
            return ConstructCoderPromptResponse(prompt="coder prompt")
        if isinstance(request, SpawnSubagentRequest):
            spawns.append(request)
            task_id = "coder-1" if request.subagent_type == "balanced-subagent" else "reviewer-1"
            return SpawnSubagentResponse(task_id=task_id, output="subagent output")
        if isinstance(request, BashRequest):
            return BashResponse(stdout="diff content", exit_code=0)
        if isinstance(request, CheckAlignmentRequest):
            alignment_checks += 1
            return CheckAlignmentResponse(aligned=alignment_checks > 1)
        if isinstance(request, GenerateAlignmentFeedbackRequest):
            return GenerateAlignmentFeedbackResponse(feedback="drift feedback")
        if isinstance(request, ConstructReviewerPromptRequest):
            return ConstructReviewerPromptResponse(prompt="reviewer prompt")
        if isinstance(request, CheckConvergenceRequest):
            return CheckConvergenceResponse(converged=True)
        raise ValueError(f"unhandled request: {request}")

    report = drive(Workflow().run(), server)

    assert report == "Converged after 0 review cycles."
    assert alignment_checks == 2
    # exactly one drift fix, resuming the coder session with the feedback
    drift_fixes = [s for s in spawns if s.description == "fix alignment drift"]
    assert len(drift_fixes) == 1
    assert drift_fixes[0].prompt == "drift feedback"
    assert drift_fixes[0].task_id == "coder-1"


def test_alignment_escalation():
    """Alignment never passes: Escalate after exactly max_align_fixes fixes."""
    feedback_count = 0

    def server(request):
        nonlocal feedback_count
        if isinstance(request, ConstructCoderPromptRequest):
            return ConstructCoderPromptResponse(prompt="coder prompt")
        if isinstance(request, SpawnSubagentRequest):
            return SpawnSubagentResponse(task_id="coder-1", output="subagent output")
        if isinstance(request, BashRequest):
            return BashResponse(stdout="diff content", exit_code=0)
        if isinstance(request, CheckAlignmentRequest):
            return CheckAlignmentResponse(aligned=False)
        if isinstance(request, GenerateAlignmentFeedbackRequest):
            feedback_count += 1
            return GenerateAlignmentFeedbackResponse(feedback="drift feedback")
        raise ValueError(f"unhandled request: {request}")

    with pytest.raises(Escalate, match="alignment failed"):
        drive(Workflow(max_align_fixes=2).run(), server)
    assert feedback_count == 2  # cap reached exactly, no extra attempts


def test_review_nonconvergence_escalation():
    """Reviewer never converges: Escalate after exactly max_review_cycles."""
    spawns = []
    convergence_checks = 0

    def server(request):
        nonlocal convergence_checks
        if isinstance(request, ConstructCoderPromptRequest):
            return ConstructCoderPromptResponse(prompt="coder prompt")
        if isinstance(request, SpawnSubagentRequest):
            spawns.append(request)
            task_id = "coder-1" if request.subagent_type == "balanced-subagent" else "reviewer-1"
            return SpawnSubagentResponse(task_id=task_id, output="1. still broken")
        if isinstance(request, BashRequest):
            return BashResponse(stdout="diff content", exit_code=0)
        if isinstance(request, CheckAlignmentRequest):
            return CheckAlignmentResponse(aligned=True)
        if isinstance(request, GenerateAlignmentFeedbackRequest):
            return GenerateAlignmentFeedbackResponse(feedback="drift feedback")
        if isinstance(request, ConstructReviewerPromptRequest):
            return ConstructReviewerPromptResponse(prompt="reviewer prompt")
        if isinstance(request, CheckConvergenceRequest):
            convergence_checks += 1
            return CheckConvergenceResponse(converged=False)
        raise ValueError(f"unhandled request: {request}")

    with pytest.raises(Escalate, match="did not converge"):
        drive(Workflow(max_review_cycles=3).run(), server)

    review_fixes = [s for s in spawns if s.description == "apply review findings"]
    assert len(review_fixes) == 3  # cap reached exactly
    assert all(s.task_id == "coder-1" for s in review_fixes)  # coder resumed
    re_reviews = [s for s in spawns if s.description == "re-review the changes"]
    assert len(re_reviews) == 3
    assert all(s.task_id == "reviewer-1" for s in re_reviews)  # reviewer resumed
    assert convergence_checks == 4  # initial check + one per fix cycle


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
