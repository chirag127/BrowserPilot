"""Task CRUD routes."""

import asyncio

from fastapi import APIRouter, HTTPException, Query

from browser_pilot.agent.action_loop import ActionLoop
from browser_pilot.logging import get_logger
from browser_pilot.models.task import Task, TaskStatus
from browser_pilot.server.schemas import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
)

logger = get_logger(__name__)
tasks_router = APIRouter()

# In-memory task store (replace with DB in production)
_task_store: dict[str, Task] = {}
_task_results: dict[str, dict] = {}
_active_tasks: dict[str, asyncio.Task] = {}


def _task_to_response(task: Task) -> TaskResponse:
    """Convert a Task model to API response."""
    result_dict = None
    if task.result:
        result_dict = {
            "success": task.result.success,
            "summary": task.result.summary,
            "extracted_data": task.result.extracted_data,
            "screenshots": task.result.screenshots,
            "total_time": task.result.total_time,
            "total_steps": task.result.total_steps,
            "errors": task.result.errors,
        }

    return TaskResponse(
        id=task.id,
        instruction=task.instruction,
        status=task.status.value,
        sub_tasks=[
            {
                "id": st.id,
                "description": st.description,
                "status": st.status.value,
                "order": st.order,
            }
            for st in task.sub_tasks
        ],
        result=result_dict,
        error=task.error,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


async def _run_task(task: Task, provider: str) -> None:
    """Background task execution."""
    try:
        task.status = TaskStatus.EXECUTING
        task.mark_updated()

        loop = ActionLoop(provider=provider)
        result = await loop.run(task)

        task.result = result
        task.status = (
            TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
        )
        task.mark_updated()

        logger.info(
            "task_finished",
            task_id=task.id,
            success=result.success,
            steps=result.total_steps,
        )
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error = str(e)
        task.mark_updated()
        logger.error("task_execution_error", task_id=task.id, error=str(e))


@tasks_router.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    """Create and start a new browser task."""
    task = Task(instruction=request.instruction)
    _task_store[task.id] = task

    # Start background execution
    bg_task = asyncio.create_task(_run_task(task, request.provider))
    _active_tasks[task.id] = bg_task

    logger.info(
        "task_created", task_id=task.id, instruction=task.instruction[:100]
    )
    return _task_to_response(task)


@tasks_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get task status and result."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_to_response(task)


@tasks_router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TaskListResponse:
    """List all tasks with pagination."""
    all_tasks = sorted(
        _task_store.values(),
        key=lambda t: t.created_at,
        reverse=True,
    )
    page = all_tasks[offset : offset + limit]

    return TaskListResponse(
        tasks=[_task_to_response(t) for t in page],
        total=len(all_tasks),
        limit=limit,
        offset=offset,
    )


@tasks_router.delete("/tasks/{task_id}", status_code=204)
async def cancel_task(task_id: str) -> None:
    """Cancel a running task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    bg_task = _active_tasks.get(task_id)
    if bg_task and not bg_task.done():
        bg_task.cancel()

    task.status = TaskStatus.CANCELLED
    task.mark_updated()
    logger.info("task_cancelled", task_id=task_id)
