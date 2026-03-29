"""Example: Search the web and extract results."""

import asyncio

from browser_pilot.agent.action_loop import ActionLoop
from browser_pilot.models.task import Task


async def main() -> None:
    """Search Hacker News and extract top posts."""
    task = Task(
        instruction=(
            "Go to news.ycombinator.com and extract the titles "
            "of the top 10 posts. Return them as a numbered list."
        )
    )

    loop = ActionLoop(provider="ollama")
    result = await loop.run(task)

    print(f"\n{'=' * 60}")
    print(f"Success: {result.success}")
    print(f"Steps: {result.total_steps}")
    print(f"Time: {result.total_time:.1f}s")
    if result.errors:
        print(f"Errors: {result.errors}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
