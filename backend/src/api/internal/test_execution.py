"""Test Execution router — /run-test, /test-result/*"""
import json
import os
import re
import html
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from api.dependencies import get_task_db_dep
from db.database import TaskDB
from config import PROJECT_ROOT


router = APIRouter(tags=["Test Execution"])


@router.get("/run-test/{task_id}")
def run_test_api(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """Execute test code via pytest and stream output via SSE"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_file = task.get("test_code_file")
    if not test_code_file:
        raise HTTPException(status_code=400, detail="No test code for this task")

    normalized = os.path.normpath(test_code_file)
    normalized_forward = normalized.replace("\\", "/")
    if ".." in normalized_forward or not normalized_forward.startswith("tests/"):
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = os.path.join(PROJECT_ROOT, normalized)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Test file not found")

    def event_generator():
        import queue
        import threading
        from services.executor import run_test

        q: queue.Queue = queue.Queue()

        def on_output(stream_type: str, content: str):
            q.put({"type": stream_type, "content": content})

        def run_in_thread():
            run_test(test_code_file, on_output)
            q.put(None)

        thread = threading.Thread(target=run_in_thread)
        thread.start()

        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/test-result/{task_id}")
def get_test_result(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """获取测试结果日志内容"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_file = task.get("test_code_file")
    if not test_code_file:
        raise HTTPException(status_code=404, detail="No test code for this task")

    normalized = os.path.normpath(test_code_file)
    normalized_forward = normalized.replace("\\", "/")
    if ".." in normalized_forward or not normalized_forward.startswith("tests/"):
        raise HTTPException(status_code=400, detail="Invalid path")

    test_code_dir = os.path.dirname(os.path.join(PROJECT_ROOT, normalized))
    results_dir = os.path.join(test_code_dir, "results")

    if not os.path.exists(results_dir):
        raise HTTPException(status_code=404, detail="No results directory found")

    log_files = [f for f in os.listdir(results_dir) if f.endswith(".log")]
    if not log_files:
        raise HTTPException(status_code=404, detail="No log file found")

    latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(results_dir, f)))
    log_path = os.path.join(results_dir, latest_log)

    test_dir = "/".join(test_code_file.split("/")[:-1])
    log_file_rel = f"{test_dir}/results/{latest_log}"

    MAX_LOG_SIZE = 1024 * 1024
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read(MAX_LOG_SIZE)
    except (FileNotFoundError, IOError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to read log file: {str(e)}")

    return {
        "status": "success",
        "log_content": log_content,
        "log_file": log_file_rel,
        "report_url": f"/test-result/{task_id}/report",
    }


@router.get("/test-result/{task_id}/report")
def get_test_report(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """返回 pytest-html 测试报告"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_file = task.get("test_code_file")
    if not test_code_file:
        raise HTTPException(status_code=404, detail="No test code for this task")

    test_code_dir = os.path.dirname(os.path.join(PROJECT_ROOT, test_code_file))
    report_path = os.path.join(test_code_dir, "results", "report.html")

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(report_path, media_type="text/html")


@router.get("/test-result/{task_id}/report-data")
def get_report_data(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """返回解析后的测试报告数据（用于可视化图表）"""
    import json as json_lib

    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_file = task.get("test_code_file")
    if not test_code_file:
        raise HTTPException(status_code=404, detail="No test code for this task")

    test_code_dir = os.path.dirname(os.path.join(PROJECT_ROOT, test_code_file))
    report_path = os.path.join(test_code_dir, "results", "report.html")

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r'data-jsonblob="([^"]+)"', content)
        if not match:
            raise HTTPException(status_code=500, detail="Failed to find report data")

        json_str = html.unescape(match.group(1))
        data = json_lib.loads(json_str)

        tests = data.get("tests", {})
        test_cases = []
        passed = failed = skipped = 0

        for test_name, test_list in tests.items():
            if not test_list:
                continue
            test_info = test_list[0]
            result = test_info.get("result", "").lower()
            status = "passed" if result == "passed" else ("failed" if result == "failed" else "skipped")

            if status == "passed":
                passed += 1
            elif status == "failed":
                failed += 1
            else:
                skipped += 1

            test_cases.append({
                "name": test_name,
                "status": status,
                "duration": test_info.get("duration", "0s"),
                "message": test_info.get("log") if status == "failed" else None,
            })

        return {
            "summary": {"total": len(test_cases), "passed": passed, "failed": failed, "skipped": skipped},
            "test_cases": test_cases,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse report: {str(e)}")
