import asyncio

from workflow import SubagentType, Workflow


class FakeSubagent:
    def __init__(self, name: str, events: list):
        self.name = name
        self.events = events
        self.resumes = []

    async def resume(self, prompt: str) -> str:
        self.resumes.append(prompt)
        self.events.append(f"resume:{self.name}")
        return f"{self.name} output"


class FakeAgent:
    def __init__(self, plan: str = "add a health endpoint"):
        self.plan = plan
        self.spawns = []
        self.events = []

    async def obtain_plan(self) -> str:
        return self.plan

    async def spawn(self, subagent_type: SubagentType, prompt: str | None = None):
        subagent = FakeSubagent(f"fake-{subagent_type.value}", self.events)
        self.spawns.append((subagent_type, subagent))
        self.events.append(f"spawn:{subagent_type.value}")
        return subagent

    async def construct_implementation_prompt(self, plan: str) -> str:
        return f"implement: {plan}"

    async def construct_review_prompt(self, plan: str) -> str:
        return f"review: {plan}"


def test_build_and_review():
    agent = FakeAgent()
    result = asyncio.run(Workflow(agent).run())

    # Two subagents spawned: coder first, reviewer second.
    assert [t for t, _ in agent.spawns] == [SubagentType.BALANCED, SubagentType.SMART]

    # Prompts built by the construct_* methods, embedding the plan.
    _, coder = agent.spawns[0]
    _, reviewer = agent.spawns[1]
    assert coder.resumes == ["implement: add a health endpoint"]
    assert reviewer.resumes == ["review: add a health endpoint"]

    # The coder implements before the reviewer reviews.
    assert agent.events == [
        "spawn:balanced",
        "spawn:smart",
        "resume:fake-balanced",
        "resume:fake-smart",
    ]

    # The workflow returns the reviewer's findings directly.
    assert result == "fake-smart output"
