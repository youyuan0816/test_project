import json
import os
from datetime import datetime


# PROJECT_DIR 是项目根目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_FILE = os.path.join(PROJECT_DIR, "sessions", "session.json")


def load_sessions():
    """加载 session 映射"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sessions(sessions):
    """保存 session 映射"""
    sessions_dir = os.path.dirname(SESSIONS_FILE)
    os.makedirs(sessions_dir, exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def get_session_id(excel_path):
    """获取 Excel 对应的 session ID"""
    sessions = load_sessions()
    entry = sessions.get(excel_path)
    return entry["session_id"] if entry else None


def save_session_id(excel_path, session_id):
    """保存 session ID"""
    sessions = load_sessions()
    sessions[excel_path] = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    }
    save_sessions(sessions)
