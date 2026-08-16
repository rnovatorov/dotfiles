import asyncio

import pytest

from workflow import SubagentType, Workflow


class FakeSubagent:
    def __init__(self, name: str, events: list):
        self.name = name
        self.events = events
        self.resumes = []

    async def resume(self, prompt: str) -> str:
        self.resumes.append(prompt)
        self.events.append(f"resume:{self.name}")
        lines = prompt.removeprefix("fizzbuzz for ").split(", ")
        return "\n".join(f"{n}: {fizzbuzz(int(n))}" for n in lines)


def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)


class FakeAgent:
    def __init__(self):
        self.spawns = []
        self.records = []
        self.events = []
        self.parsed = []
        self._counter = 0

    async def spawn(self, subagent_type: SubagentType, prompt: str | None = None):
        self._counter += 1
        subagent = FakeSubagent(f"fake-{self._counter}", self.events)
        self.spawns.append((subagent_type, subagent))
        self.events.append(f"spawn:{subagent_type.value}")
        return subagent

    async def construct_fizzbuzz_prompt(self, batch: list[int]) -> str:
        return f"fizzbuzz for {', '.join(map(str, batch))}"

    async def parse_batch_results(self, batch: list[int], response: str):
        mapping = {}
        for line in response.splitlines():
            n, result = line.split(": ")
            mapping[int(n)] = result
        self.parsed.append(mapping)
        return mapping

    async def record(self, n: int, result: str) -> None:
        self.records.append((n, result))


def test_fizzbuzz_batching():
    agent = FakeAgent()
    result = asyncio.run(Workflow(agent, count=15, batch_size=4).run())

    assert result == "FizzBuzz complete for 1 to 15."

    # One fast subagent per batch: ceil(15/4) = 4 batches.
    assert [t for t, _ in agent.spawns] == [SubagentType.FAST] * 4
    for (_, subagent), batch in zip(agent.spawns, [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15]]):
        assert len(subagent.resumes) == 1
        assert subagent.resumes[0] == f"fizzbuzz for {', '.join(map(str, batch))}"

    # Results recorded in order, one entry per number.
    assert [n for n, _ in agent.records] == list(range(1, 16))
    expected = [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz",
    ]
    assert [r for _, r in agent.records] == expected


def test_default_batching_splits_100_into_5():
    agent = FakeAgent()
    result = asyncio.run(Workflow(agent).run())

    assert result == "FizzBuzz complete for 1 to 100."
    assert len(agent.spawns) == 5
    assert [n for n, _ in agent.records] == list(range(1, 101))
    assert agent.records[14] == (15, "FizzBuzz")
    assert agent.records[29] == (30, "FizzBuzz")
