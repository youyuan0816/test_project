import argparse
import json
import sqlite3
import sys
import os

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def migrate_sessions():
    """从 session.json 迁移到数据库"""
    from db.database import get_task_db

    json_file = os.path.join(os.path.dirname(__file__), "..", "sessions", "session.json")
    if not os.path.exists(json_file):
        print("No session.json found, skipping migration")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            print("session.json is empty, skipping migration")
            return
        sessions_data = json.loads(content)

    task_db = get_task_db()
    migrated = 0
    skipped = 0

    for excel_path, info in sessions_data.items():
        # Check if task exists for this excel_path
        with sqlite3.connect(task_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE result_file = ? AND deleted_at IS NULL",
                (excel_path,)
            )
            row = cursor.fetchone()

        if not row:
            print(f"Skipping {excel_path}: no associated task")
            skipped += 1
            continue

        task_id = row[0]
        existing = task_db.get_session(task_id)
        if existing:
            print(f"Skipping {excel_path}: session already exists")
            skipped += 1
            continue

        success = task_db.create_session(
            task_id=task_id,
            session_id=info.get("session_id"),
            excel_path=excel_path,
            title=info.get("title"),
            time_created=info.get("time_created"),
            time_updated=info.get("time_updated")
        )
        if success:
            print(f"Migrated {excel_path}")
            migrated += 1
        else:
            print(f"Failed to migrate {excel_path}")
            skipped += 1

    print(f"Migration complete: {migrated} migrated, {skipped} skipped")


def main():
    parser = argparse.ArgumentParser(description='OpenCode Session Manager')
    parser.add_argument('--generate', action='store_true', help='生成 Excel 测试用例')
    parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE',
                        help='继续 session，读取 Excel 生成测试代码')
    parser.add_argument('--migrate-sessions', action='store_true',
                        help='从 session.json 迁移到数据库')
    args = parser.parse_args()

    if args.migrate_sessions:
        migrate_sessions()
    elif args.generate:
        from services.generator import generate_excel
        generate_excel()
    elif args.continue_file:
        from services.generator import continue_session
        continue_session(args.continue_file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
