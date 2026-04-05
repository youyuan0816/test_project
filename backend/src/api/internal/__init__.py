"""Internal routers package."""
from .generation import router as generation_router
from .tasks import router as tasks_router
from .sessions import router as sessions_router
from .testcases import router as testcases_router
from .test_execution import router as test_execution_router
from .system import router as system_router

__all__ = [
    "generation_router",
    "tasks_router",
    "sessions_router",
    "testcases_router",
    "test_execution_router",
    "system_router",
]
