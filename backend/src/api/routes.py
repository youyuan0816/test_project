"""App creation and router assembly."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from .internal import (
    generation_router,
    tasks_router,
    sessions_router,
    testcases_router,
    test_execution_router,
    system_router,
)


app = FastAPI(title="UI Test Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation_router)
app.include_router(tasks_router)
app.include_router(sessions_router)
app.include_router(testcases_router)
app.include_router(test_execution_router)
app.include_router(system_router)
