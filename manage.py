"""
Project manage tasks for CLI automation.
"""

import subprocess  # nosec B404 - legitimate use of subprocess for dev tools


def format() -> None:
    """Run Ruff linting and formatting."""
    commands = [
        ["uv", "run", "ruff", "format", "."],
        ["uv", "run", "ruff", "check", ".", "--fix"],
        ["echo", "\n🟢 Linting → ✅ Code clean\n"],
    ]
    for cmd in commands:
        subprocess.run(cmd, check=True)  # nosec B603,B607 - trusted dev commands


def test() -> None:
    """Run tests with pytest."""
    commands = [
        ["uv", "run", "pytest", "-q"],
        ["echo", "\n🟢 Test Coverage → ✅ Test coverage sufficient\n"],
    ]
    for cmd in commands:
        subprocess.run(cmd, check=True)  # nosec B603,B607 - trusted dev commands
