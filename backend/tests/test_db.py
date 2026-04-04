import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import TaskDB

def test_create_and_get_task():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = TaskDB(db_path)

        task_id = db.create_task(
            name="test.xlsx",
            task_type="generate_excel",
            url="https://example.com",
            description="Test task",
        )

        task = db.get_task(task_id)
        assert task is not None
        assert task["name"] == "test.xlsx"
        assert task["task_type"] == "generate_excel"
        assert task["status"] == "pending"

        db.close()
    finally:
        os.unlink(db_path)

def test_update_task_status():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = TaskDB(db_path)

        task_id = db.create_task(name="test.xlsx", task_type="generate_excel", url="", description="")
        db.update_task_status(task_id, "running")

        task = db.get_task(task_id)
        assert task["status"] == "running"

        db.close()
    finally:
        os.unlink(db_path)

def test_list_tasks():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = TaskDB(db_path)

        db.create_task(name="task1.xlsx", task_type="generate_excel", url="", description="")
        db.create_task(name="task2.xlsx", task_type="generate_code", url="", description="")

        tasks = db.list_tasks()
        assert len(tasks) == 2

        db.close()
    finally:
        os.unlink(db_path)