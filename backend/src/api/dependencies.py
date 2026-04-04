from db.database import get_task_db, TaskDB


def get_task_db_dep() -> TaskDB:
    """Dependency injection for TaskDB"""
    return get_task_db()
