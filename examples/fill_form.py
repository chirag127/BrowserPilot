"""Example: Fill out a web form."""

import asyncio

from browser_pilot.agent.action_loop import ActionLoop
from browser_pilot.models.task import Task


async def main() -> None:
    """Fill a contact form on a test page."""
    task = Task(
        instruction=(
            "Go to https://httpbin.org/forms/post and fill the form: "
            "Customer name: John Doe, "
            "Telephone: 555-1234, "
            "E-mail: john@example.com, "
            "Size: Medium, "
            "Delivery time: 12:00, "
            "Comments: Test submission from BrowserPilot, "
            "then click submit."
        )
    )

    loop = ActionLoop(provider="ollama")
    result = await loop.run(task)

    print(f"\n{'=' * 60}")
    print(f"Success: {result.success}")
    print(f"Steps: {result.total_steps}")
    print(f"Time: {result.total_time:.1f}s")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
