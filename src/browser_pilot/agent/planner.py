"""Task planner — decomposes instructions into sub-tasks."""

import json
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger
from browser_pilot.models.task import SubTask, Task
from browser_pilot.vision.prompts import PLANNER_SYSTEM_PROMPT

logger = get_logger(__name__)


class Planner:
    """Decompose user instructions into atomic sub-tasks."""

    def __init__(self, provider: str = "ollama") -> None:
        self._settings = get_settings()
        self._provider = provider
        self._llm = ChatOpenAI(
            model=self._settings.get_llm_model(provider),
            base_url=self._settings.get_llm_base_url(provider),
            api_key=self._settings.get_llm_api_key(provider),
            max_tokens=2048,
            temperature=0.1,
        )

    async def plan(self, task: Task) -> Task:
        """Decompose a task instruction into sub-tasks.

        Args:
            task: Task with instruction to decompose.

        Returns:
            Task with populated sub_tasks list.
        """
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Break down this browser task into sub-tasks:\n\n"
                    f'"{task.instruction}"'
                ),
            ),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            sub_tasks = self._parse_plan(response.content, task.id)

            task.sub_tasks = sub_tasks
            logger.info(
                "task_planned",
                task_id=task.id,
                sub_task_count=len(sub_tasks),
            )
            return task

        except Exception as e:
            logger.error("planning_error", error=str(e))
            # Fallback: single sub-task from instruction
            task.sub_tasks = [
                SubTask(
                    description=task.instruction,
                    order=0,
                    parent_task_id=task.id,
                )
            ]
            return task

    def _parse_plan(self, content: str, task_id: str) -> list[SubTask]:
        """Parse LLM response into SubTask objects."""
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())
        raw_tasks = data.get("sub_tasks", [])

        sub_tasks = []
        for i, st in enumerate(raw_tasks):
            sub_tasks.append(
                SubTask(
                    description=st.get("description", f"Step {i + 1}"),
                    order=i,
                    parent_task_id=task_id,
                )
            )

        # Cap at 10 sub-tasks
        return sub_tasks[:10]
