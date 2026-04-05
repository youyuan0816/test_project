"""Test Cases router — /testcases, /download-code/{task_id}"""
import os
import io
import zipfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.models import TestCaseResponse, TestCasesListResponse
from api.dependencies import get_task_db_dep
from db.database import TaskDB
from config import PROJECT_ROOT


router = APIRouter(tags=["Test Cases"])


@router.get("/testcases", response_model=TestCasesListResponse)
def get_testcases(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取所有生成了测试代码的 Task 列表"""
    tasks = task_db.list_tasks()
    testcases = [
        TestCaseResponse(
            task_id=t["id"],
            name=t["name"],
            excel_file=t.get("result_file"),
            test_code_dir=t.get("test_code_file"),
            created_at=t["created_at"],
        )
        for t in tasks
        if t.get("test_code_file") and t.get("status") == "completed"
    ]
    return TestCasesListResponse(testcases=testcases)


@router.get("/download-code/{task_id}")
def download_test_code(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """下载测试代码目录（zip 格式）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_dir = task.get("test_code_file")
    if not test_code_dir:
        raise HTTPException(status_code=404, detail="No test code for this task")

    normalized = os.path.normpath(test_code_dir)
    normalized_forward = normalized.replace("\\", "/")
    if ".." in normalized_forward or not normalized_forward.startswith("tests/"):
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = os.path.join(PROJECT_ROOT, normalized)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        if os.path.isdir(full_path):
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, PROJECT_ROOT)
                    zipf.write(file_path, arcname)
        else:
            arcname = os.path.relpath(full_path, PROJECT_ROOT)
            zipf.write(full_path, arcname)

    zip_buffer.seek(0)

    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(test_code_dir)}.zip"},
    )
