"""Core action loop — the observe-decide-act cycle."""

import asyncio
import time
from typing import Optional

from browser_pilot.agent.critic import Critic
from browser_pilot.agent.memory import AgentMemory
from browser_pilot.agent.planner import Planner
from browser_pilot.agent.state import AgentStateMachine, AgentState
from browser_pilot.browser.actions import BrowserActions
from browser_pilot.browser.controller import BrowserController
from browser_pilot.browser.dom_inspector import DOMInspector
from browser_pilot.config import get_settings
from browser_pilot.logging import get_logger
from browser_pilot.models.action import Action, ActionStatus
from browser_pilot.models.dom import DOMElement
from browser_pilot.models.result import ExecutionResult, StepResult
from browser_pilot.models.task import SubTask, Task, TaskStatus
from browser_pilot.vision.annotator import DOMAnnotator
from browser_pilot.vision.grounding import ActionGrounder
from browser_pilot.vision.interpreter import VisionInterpreter
from browser_pilot.vision.screenshot import ScreenshotCapture

logger = get_logger(__name__)


class ActionLoop:
    """Main observe-decide-act loop for browser automation.

    Orchestrates the full agent pipeline:
    1. Plan — decompose task into sub-tasks
    2. For each sub-task:
       a. Observe — screenshot + DOM extraction
       b. Annotate — overlay element markers
       c. Decide — LLM picks next action
       d. Ground — verify action against live DOM
       e. Act — execute the action
       f. Validate — critic checks completion
    3. Return execution result
    """

    def __init__(
        self,
        provider: str = "ollama",
    ) -> None:
        self._settings = get_settings()
        self._provider = provider

        self._browser = BrowserController()
        self._dom = DOMInspector()
        self._annotator = DOMAnnotator()
        self._screenshot = ScreenshotCapture()
        self._interpreter = VisionInterpreter(provider=provider)
        self._grounder = ActionGrounder()
        self._critic = Critic(provider=provider)
        self._planner = Planner(provider=provider)
        self._memory = AgentMemory()
        self._state = AgentStateMachine()

    async def run(self, task: Task) -> ExecutionResult:
        """Execute a task end-to-end.

        Args:
            task: The task to execute.

        Returns:
            ExecutionResult with full execution details.
        """
        start_time = time.monotonic()
        result = ExecutionResult(
            task_id=task.id,
            instruction=task.instruction,
        )

        try:
            # Start browser
            await self._browser.start()
            self._state.transition(AgentState.PLANNING)

            # Plan
            task = await self._planner.plan(task)
            task.status = TaskStatus.EXECUTING

            # Execute each sub-task
            for sub_task in task.sub_tasks:
                if self._state.is_terminal:
                    break

                self._state.transition(AgentState.EXECUTING)
                step_result = await self._execute_sub_task(sub_task)

                if step_result.success:
                    result.steps.append(step_result)
                else:
                    result.errors.append(step_result.error or "Unknown error")
                    if self._state.failure_count >= self._settings.max_failures:
                        self._state.transition(AgentState.FAILED)
                        break

            # Compile result
            if self._state.current_state != AgentState.FAILED:
                self._state.transition(AgentState.COMPLETED)

            result.success = self._state.current_state == AgentState.COMPLETED
            result.total_time = time.monotonic() - start_time
            result.total_steps = self._state.step_count
            result.screenshots = self._screenshot.get_screenshot_paths()

            logger.info(
                "task_completed",
                task_id=task.id,
                success=result.success,
                steps=result.total_steps,
                time=round(result.total_time, 2),
            )

            return result

        except Exception as e:
            logger.error("action_loop_error", error=str(e))
            self._state.transition(AgentState.FAILED)
            result.success = False
            result.errors.append(str(e))
            result.total_time = time.monotonic() - start_time
            return result

        finally:
            await self._browser.stop()

    async def _execute_sub_task(self, sub_task: SubTask) -> StepResult:
        """Execute a single sub-task with the observe-decide-act loop."""
        start = time.monotonic()
        action_history: list[str] = []
        current_elements: list[DOMElement] = []

        for step in range(self._settings.max_steps):
            if self._state.is_terminal:
                break

            try:
                # OBSERVE
                self._state.transition(AgentState.OBSERVING)
                screenshot_bytes = await self._screenshot.capture(
                    self._browser.page
                )
                current_elements = await self._dom.inspect(self._browser.page)

                # Annotate
                annotated_bytes = self._annotator.annotate(
                    screenshot_bytes, current_elements
                )
                screenshot_b64 = self._screenshot.to_base64(annotated_bytes)
                element_summary = self._annotator.get_element_summary(
                    current_elements
                )

                # DECIDE
                self._state.transition(AgentState.DECIDING)
                page_url = await self._browser.get_current_url()
                page_title = await self._browser.get_title()

                action = await self._interpreter.interpret(
                    screenshot_b64=screenshot_b64,
                    element_summary=element_summary,
                    task_description=sub_task.description,
                    action_history=action_history,
                    page_url=page_url,
                    page_title=page_title,
                )

                # GROUND
                self._state.transition(AgentState.GROUNDING)
                is_valid, confidence, reason = await self._grounder.verify(
                    action, self._browser.page, current_elements
                )

                if not is_valid:
                    logger.warning(
                        "action_rejected",
                        reason=reason,
                        confidence=confidence,
                    )
                    self._state.transition(AgentState.RECOVERING)
                    action_history.append(
                        f"REJECTED: {action.action_type.value} "
                        f"(reason: {reason})"
                    )
                    continue

                # ACT
                self._state.transition(AgentState.ACTING)
                actions = BrowserActions(self._browser.page)
                action_result = await actions.execute(action, current_elements)

                if action_result.success:
                    action_desc = (
                        f"{action.action_type.value}"
                        f"(element={action.target_element_index})"
                    )
                    if action.params.get("text"):
                        action_desc += f' text="{action.params["text"][:30]}"'
                    action_history.append(action_desc)
                    self._memory.add_action(action_desc)

                    # Check if sub-task is done
                    if action.action_type.value == "extract":
                        break
                else:
                    self._state.transition(AgentState.RECOVERING)
                    action_history.append(
                        f"FAILED: {action.action_type.value} "
                        f"- {action_result.error}"
                    )

                # VALIDATE — check completion with critic
                if step > 0 and step % 3 == 0:
                    self._state.transition(AgentState.VALIDATING)
                    page_text = await self._dom.get_page_text(
                        self._browser.page
                    )
                    critic_result = await self._critic.evaluate(
                        sub_task_description=sub_task.description,
                        action_history=action_history,
                        page_url=page_url,
                        page_title=page_title,
                        page_text=page_text,
                    )

                    if critic_result.is_done:
                        logger.info(
                            "sub_task_completed",
                            description=sub_task.description[:100],
                        )
                        break

            except asyncio.TimeoutError:
                logger.warning("step_timeout", step=step)
                self._state.transition(AgentState.RECOVERING)
                continue
            except Exception as e:
                logger.error("step_error", step=step, error=str(e))
                self._state.transition(AgentState.RECOVERING)
                action_history.append(f"ERROR: {e}")
                continue

        # Final validation
        self._state.transition(AgentState.VALIDATING)
        return StepResult(
            step_number=self._state.step_count,
            action_type="sub_task_complete",
            success=True,
            elapsed_seconds=time.monotonic() - start,
            reasoning=f"Sub-task: {sub_task.description[:100]}",
        )

    async def cancel(self) -> None:
        """Cancel the running task."""
        self._state.transition(AgentState.CANCELLED)
        logger.info("task_cancelled")
