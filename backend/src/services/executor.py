import subprocess
import os
import threading
import time
import json
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_name = os.path.splitext(os.path.basename(test_code_path))[0]

    # Save log file in tests/{save_path}/results/ directory
    test_code_dir = os.path.dirname(full_path)
    results_dir = Path(test_code_dir) / "results"
    os.makedirs(results_dir, exist_ok=True)
    result_log = results_dir / f"{task_name}_{timestamp}.log"

    cmd = [
        sys.executable, "-u", "-m", "pytest",
        test_code_path, "-v", "--tb=short",
        "--alluredir", str(results_dir / "allure-results")
    ]

    start_time = time.time()
    try:
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )

        passed = 0
        failed = 0

        with open(result_log, "w", encoding="utf-8") as log_file:
            for line in iter(process.stdout.readline, b""):
                if line:
                    decoded = line.decode("utf-8", errors="replace")
                    log_file.write(decoded)
                    log_file.flush()
                    on_output("stdout", decoded.rstrip())

                if b" PASSED" in line:
                    passed += 1
                elif b" FAILED" in line:
                    failed += 1

                if time.time() - start_time > timeout:
                    process.kill()
                    on_output("stderr", f"\n[TIMEOUT] Test execution exceeded {timeout} seconds")
                    break

            process.wait()

        # Generate Allure report
        allure_results_dir = results_dir / "allure-results"
        allure_report_dir = results_dir / "allure-report"

        if allure_results_dir.exists():
            try:
                subprocess.run(
                    ["allure", "generate", str(allure_results_dir), "-o", str(allure_report_dir)],
                    capture_output=True,
                    timeout=60
                )
                print(f"[INFO] Allure report generated: {allure_report_dir}")
            except Exception as e:
                print(f"[WARN] Failed to generate Allure report: {e}")

        duration = f"{time.time() - start_time:.1f}s"

    except Exception as e:
        result = {"status": "error", "message": str(e)}
        on_output("result", json.dumps(result))
        return result

    result = {
        "status": "success",
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "log_file": str(result_log)
    }
    on_output("result", json.dumps(result))
    return result
