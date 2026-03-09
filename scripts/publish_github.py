from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=BASE_DIR, check=check, text=True, capture_output=True)


def has_changes() -> bool:
    result = run(["git", "status", "--porcelain"], check=False)
    return bool(result.stdout.strip())


def main() -> None:
    run(["git", "add", "."])
    if not has_changes():
        print("No changes to commit.")
        return
    msg = f"chore: auto update daily report {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    commit = run(["git", "commit", "-m", msg], check=False)
    print(commit.stdout.strip() or commit.stderr.strip())
    push = run(["git", "push"], check=False)
    print(push.stdout.strip() or push.stderr.strip())


if __name__ == '__main__':
    main()
