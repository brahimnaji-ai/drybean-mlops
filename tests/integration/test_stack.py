from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_local_stack_smoke_check() -> None:
    bash = "bash"
    if os.name == "nt":
        git_bash = (
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Git" / "bin" / "bash.exe"
        )
        if git_bash.is_file():
            bash = str(git_bash)

    result = subprocess.run(
        [bash, "scripts/smoke_stack.sh"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
