from typing import Optional, List
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    url: str
    filepath: str
    username: Optional[str] = ""
    password: Optional[str] = ""
    description: str
    continue_excel: Optional[str] = None


class ContinueRequest(BaseModel):
    excel_file: str


class TaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    url: str
    description: str
    status: str
    phase: str
    session_id: Optional[str]
    result_file: Optional[str]
    result_message: Optional[str]
    created_at: str
    completed_at: Optional[str]


class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]


class CreateTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
