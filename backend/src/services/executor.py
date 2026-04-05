import subprocess
import os
import threading
import time
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROJECT_ROOT, RESULTS_DIR

def run_test(
    test_code_path: str,
    on_output: Callable[[str, str], None],  # (stream_type, content)
    timeout: int = 300
) -> dict:
    """Run pytest on test file and stream output via callback."""
    full_path = os.path.join(PROJECT_ROOT, test_code_path)
    if not os.path.exists(full_path):
        return {"status": "error", "message": f"Test file not found: {test_code_path}"}

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_name = os.path.splitext(os.path.basename(test_code_path))[0]
    result_log = RESULTS_DIR / f"{task_name}_{timestamp}.log"

    cmd = [sys.executable, "-m", "pytest", test_code_path, "-v", "--tb=short"]

    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        passed = 0
        failed = 0

        with open(result_log, "w", encoding="utf-8") as log_file:
            for line in iter(process.stdout.readline, ""):
                if line:
                    log_file.write(line)
                    log_file.flush()
                    on_output("stdout", line.rstrip())

                if " PASSED" in line:
                    passed += 1
                elif " FAILED" in line:
                    failed += 1

                if time.time() - start_time > timeout:
                    process.kill()
                    on_output("stderr", f"\n[TIMEOUT] Test execution exceeded {timeout} seconds")
                    break

            process.wait()

        duration = f"{time.time() - start_time:.1f}s"

    except Exception as e:
        return {"status": "error", "message": str(e)}

    return {
        "status": "success",
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "log_file": str(result_log)
    }
