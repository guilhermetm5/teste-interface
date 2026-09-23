import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERSION_FILE = PROJECT_ROOT / "version.json"


def get_local_commit() -> str | None:
    """Retorna o hash do commit atual: via git (se rodando de um clone)
    ou via version.json (fallback para pasta baixada sem .git)."""
    git_dir = PROJECT_ROOT / ".git"
    if git_dir.exists():
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass

    if VERSION_FILE.exists():
        try:
            data = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
            return data.get("commit")
        except (json.JSONDecodeError, OSError):
            pass

    return None
