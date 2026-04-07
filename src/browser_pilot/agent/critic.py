"""Critic sub-agent — validates task completion."""

import json
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger
from browser_pilot.vision.prompts import CRITIC_SYSTEM_PROMPT

logger = get_logger(__name__)


class CriticResult:
    """Result of critic evaluation."""

    def __init__(
        self,
        status: Literal["PASS", "FAIL", "PARTIAL"],
        reasoning: str,
        suggestion: str = "",
    ) -> None:
        self.status = status
        self.reasoning = reasoning
        self.suggestion = suggestion

    @property
    def is_done(self) -> bool:
        return self.status == "PASS"


class Critic:
    """Validates whether a sub-task has been completed."""

    def __init__(self, provider: str = "gemini") -> None:
        self._settings = get_settings()
        if provider == "gemini":
            self._llm = ChatGoogleGenerativeAI(
                model=self._settings.get_llm_model("gemini"),
                google_api_key=self._settings.get_llm_api_key("gemini"),
                max_output_tokens=1024,
                temperature=0.1,
            )
        else:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=self._settings.get_llm_model(provider),
                base_url=self._settings.get_llm_base_url(provider),
                api_key=self._settings.get_llm_api_key(provider),
                max_tokens=1024,
                temperature=0.1,
            )

    async def evaluate(
        self,
        sub_task_description: str,
        action_history: list[str],
        page_url: str = "",
        page_title: str = "",
        page_text: str = "",
    ) -> CriticResult:
        """Evaluate whether a sub-task is complete.

        Args:
            sub_task_description: Description of the sub-task.
            action_history: Actions taken so far.
            page_url: Current page URL.
            page_title: Current page title.
            page_text: Current visible page text.

        Returns:
            CriticResult with PASS/FAIL/PARTIAL status.
        """
        history_str = (
            "\n".join(
                f"  {i + 1}. {a}" for i, a in enumerate(action_history[-5:])
            )
            or "  (no actions)"
        )

        user_prompt = f"""## Sub-Task
{sub_task_description}

## Current Page State
URL: {page_url}
Title: {page_title}
Visible Text (excerpt): {page_text[:1000]}

## Actions Taken
{history_str}

Has this sub-task been completed? Respond with JSON only."""

        messages = [
            SystemMessage(content=CRITIC_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            result = self._parse_response(response.content)
            logger.info(
                "critic_evaluated",
                status=result.status,
                reasoning=result.reasoning[:200],
            )
            return result
        except Exception as e:
            logger.error("critic_error", error=str(e))
            # Default to FAIL on error to keep the loop running
            return CriticResult(
                status="FAIL",
                reasoning=f"Critic error: {e}",
            )

    def _parse_response(self, content) -> CriticResult:
        """Parse critic response."""
        # Handle both string and list responses (Gemini API can return list)
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        content = content.strip()
        # Extract JSON block if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        elif "{" in content and "}" in content:
            # Extract JSON object even without markdown formatting
            start = content.find("{")
            end = content.rfind("}") + 1
            content = content[start:end]

        data = json.loads(content.strip())

        status = data.get("status", "FAIL").upper()
        if status not in ("PASS", "FAIL", "PARTIAL"):
            status = "FAIL"

        return CriticResult(
            status=status,
            reasoning=data.get("reasoning", ""),
            suggestion=data.get("suggestion", ""),
        )
