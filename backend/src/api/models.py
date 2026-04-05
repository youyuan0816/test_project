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
    task_id: Optional[str] = None  # 可选：复用现有 task


class TaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    url: str
    description: str
    status: str
    phase: Optional[str]
    session_id: Optional[str]
    result_file: Optional[str]
    result_message: Optional[str]
    created_at: str
    completed_at: Optional[str]
    deleted_at: Optional[str]


class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]


class CreateTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TestCaseResponse(BaseModel):
    task_id: str
    name: str
    excel_file: Optional[str]
    test_code_dir: Optional[str]
    created_at: str


class TestCasesListResponse(BaseModel):
    testcases: List[TestCaseResponse]
