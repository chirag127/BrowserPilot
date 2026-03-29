"""Vision interpreter — sends screenshots to LLM for action decisions."""

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger
from browser_pilot.models.action import Action, ActionType
from browser_pilot.vision.prompts import (
    ACTOR_SYSTEM_PROMPT,
    build_user_prompt,
)

logger = get_logger(__name__)


class VisionInterpreter:
    """Uses a vision-capable LLM to interpret screenshots and decide actions."""

    def __init__(
        self,
        provider: str = "ollama",
    ) -> None:
        self._settings = get_settings()
        self._provider = provider
        self._llm = self._create_llm()

    def _create_llm(self) -> ChatOpenAI:
        """Create an LLM client for the specified provider."""
        settings = self._settings
        return ChatOpenAI(
            model=settings.get_llm_model(self._provider),
            base_url=settings.get_llm_base_url(self._provider),
            api_key=settings.get_llm_api_key(self._provider),
            max_tokens=2048,
            temperature=0.1,
        )

    async def interpret(
        self,
        screenshot_b64: str,
        element_summary: str,
        task_description: str,
        action_history: list[str],
        page_url: str = "",
        page_title: str = "",
    ) -> Action:
        """Analyze screenshot and decide the next action.

        Args:
            screenshot_b64: Base64-encoded annotated screenshot.
            element_summary: Text summary of interactive DOM elements.
            task_description: Current sub-task description.
            action_history: List of previous actions taken.
            page_url: Current page URL.
            page_title: Current page title.

        Returns:
            Action to execute next.
        """
        user_prompt = build_user_prompt(
            element_summary=element_summary,
            task_description=task_description,
            action_history=action_history,
            page_url=page_url,
            page_title=page_title,
        )

        messages = [
            SystemMessage(content=ACTOR_SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                ],
            ),
        ]

        try:
            response = await self._llm.ainvoke(messages)
            action = self._parse_response(response.content)
            logger.info(
                "action_decided",
                action_type=action.action_type.value,
                confidence=action.confidence,
                reasoning=action.reasoning[:200],
            )
            return action
        except Exception as e:
            logger.error("vision_interpret_error", error=str(e))
            # Try fallback provider
            if self._provider == "ollama":
                logger.info("trying_openrouter_fallback")
                fallback = VisionInterpreter(provider="openrouter")
                return await fallback.interpret(
                    screenshot_b64,
                    element_summary,
                    task_description,
                    action_history,
                    page_url,
                    page_title,
                )
            raise

    def _parse_response(self, content: str) -> Action:
        """Parse LLM response into an Action object."""
        import json

        try:
            # Try to extract JSON from the response
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            action_type_str = data.get("action", "wait").lower()
            try:
                action_type = ActionType(action_type_str)
            except ValueError:
                action_type = ActionType.WAIT

            return Action(
                action_type=action_type,
                params=data.get("params", {}),
                target_element_index=data.get("element_index"),
                confidence=data.get("confidence", 0.5),
                reasoning=data.get("reasoning", ""),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(
                "response_parse_fallback",
                error=str(e),
                content=content[:500],
            )
            return Action(
                action_type=ActionType.WAIT,
                params={"seconds": 2},
                confidence=0.1,
                reasoning=f"Parse error: {e}",
            )

    async def switch_provider(self, provider: str) -> None:
        """Switch to a different LLM provider."""
        self._provider = provider
        self._llm = self._create_llm()
        logger.info("llm_provider_switched", provider=provider)
