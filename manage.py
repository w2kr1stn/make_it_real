"""
Project manage tasks for CLI automation.
"""

import subprocess  # nosec B404 - legitimate use of subprocess for dev tools


def lint() -> None:
    """Run Ruff linting and formatting."""
    commands = [
        ["uv", "run", "ruff", "check", ".", "--fix"],
        ["uv", "run", "ruff", "format", "."],
        ["echo", "🟢 Linting → ✅ Code clean"],
    ]
    for cmd in commands:
        subprocess.run(cmd, check=True)  # nosec B603,B607 - trusted dev commands
