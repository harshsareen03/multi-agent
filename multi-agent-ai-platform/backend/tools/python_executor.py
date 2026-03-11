from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from langchain_core.tools import tool


@tool
def python_executor(code: str) -> dict[str, object]:
    """Execute Python code in a subprocess and return stdout, stderr, and exit code."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as handle:
        handle.write(code)
        script_path = Path(handle.name)
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    script_path.unlink(missing_ok=True)
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


class PythonExecutorTool:
    def run(self, code: str) -> dict[str, object]:
        return python_executor.invoke({"code": code})

