from __future__ import annotations

import asyncio
import enum
from typing import Protocol


class Workflow:
    """FizzBuzz: split the range into batches, compute each batch with a
    subagent concurrently, then record."""

    def __init__(self, agent: Agent, count: int = 100, batch_size: int = 20) -> None:
        self.agent = agent
        self.count = count
        self.batch_size = batch_size

    async def run(self) -> str:
        """Compute all batches concurrently, record in order, report."""

        async def fizzbuzz(batch: list[int]) -> dict[int, str]:
            subagent = await self.agent.spawn(SubagentType.FAST)
            response = await subagent.resume(
                await self.agent.construct_fizzbuzz_prompt(batch)
            )
            return await self.agent.parse_batch_results(batch, response)

        numbers = list(range(1, self.count + 1))
        batches = [
            numbers[i : i + self.batch_size]
            for i in range(0, len(numbers), self.batch_size)
        ]
        results: dict[int, str] = {}
        for mapping in await asyncio.gather(*[fizzbuzz(b) for b in batches]):
            results.update(mapping)
        for n in numbers:
            await self.agent.record(n, results[n])
        return f"FizzBuzz complete for 1 to {self.count}."


class Subagent(Protocol):

    async def resume(self, prompt: str) -> str:
        """Resume this subagent with new instructions.

        The subagent sees nothing of your conversation; the prompt must
        be self-contained.

        Args:
            prompt: The instructions for the subagent.

        Returns:
            The subagent's output text.
        """


class Agent(Protocol):

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

    async def construct_fizzbuzz_prompt(self, batch: list[int]) -> str:
        """Write the instructions for the subagent computing FizzBuzz
        for a batch of numbers.

        The prompt must be self-contained: list every number in the
        batch, instruct the subagent to return, for each n, 'FizzBuzz'
        if n % 15 == 0, 'Fizz' if n % 3 == 0, 'Buzz' if n % 5 == 0,
        otherwise str(n), as 'n: result' lines in batch order.
        """

    async def parse_batch_results(self, batch: list[int], response: str) -> dict[int, str]:
        """Parse a batch subagent's response into a number-to-result
        mapping.

        The response is 'n: result' lines. Return a dict covering
        every n in the batch. If any line is missing, malformed, or
        contradicts the FizzBuzz rules, raise ValueError naming the
        offending line.
        """

    async def record(self, n: int, result: str) -> None:
        """Record the FizzBuzz result for n to /tmp/opencode/fizzbuzz.txt,
        one line per number, appending."""


class SubagentType(enum.Enum):

    FAST = "fast"
    BALANCED = "balanced"
    SMART = "smart"
