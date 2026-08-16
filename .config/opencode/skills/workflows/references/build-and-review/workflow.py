from __future__ import annotations

import enum
from typing import Protocol


class Workflow:
    """Build-and-review: one subagent implements a plan, another reviews it."""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    async def run(self) -> str:
        """Implement the plan, review the implementation, report findings."""
        plan = await self.agent.obtain_plan()

        coder = await self.agent.spawn(SubagentType.BALANCED)
        reviewer = await self.agent.spawn(SubagentType.SMART)

        await coder.resume(await self.agent.construct_implementation_prompt(plan))
        return await reviewer.resume(await self.agent.construct_review_prompt(plan))


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

    async def obtain_plan(self) -> str:
        """Determine the plan this run should implement.

        Identify the plan from the conversation with the user; ask them
        to choose if several are on the table. Return the plan as text.
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

    async def construct_implementation_prompt(self, plan: str) -> str:
        """Write the initial instructions for the coder.

        They must be self-contained (the coder sees nothing else):
        include the full plan and instruct the coder to implement it
        and report when done.
        """

    async def construct_review_prompt(self, plan: str) -> str:
        """Write the instructions for the reviewer.

        They must be self-contained: instruct the reviewer to inspect
        the repository state (e.g. git diff, git status) against the
        full plan included in the instructions, find real defects
        (correctness, edge cases, test gaps, security), and reply with
        a numbered findings list — an empty response means no defects
        were found.
        """


class SubagentType(enum.Enum):

    FAST = "fast"
    BALANCED = "balanced"
    SMART = "smart"
