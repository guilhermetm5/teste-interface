import json
import os
import subprocess
import sys
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


def pull_latest() -> tuple[bool, str]:
    """Baixa a versão mais nova via `git pull` (requer clone git)."""
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        return False, "Pasta atual não é um clone git; não é possível atualizar automaticamente."

    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)

    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip()

    return True, result.stdout.strip()


def restart_app() -> None:
    """Encerra e reabre o processo atual, para carregar o código atualizado."""
    if os.name == "nt":
        # No Windows, os.execv não coloca aspas nos argumentos: com o Python em
        # "C:\Program Files\..." o novo processo quebra o caminho no espaço.
        # Popen recebe a lista e monta a linha de comando com as aspas certas.
        subprocess.Popen([sys.executable, *sys.argv], cwd=os.getcwd())
        os._exit(0)
    os.execv(sys.executable, [sys.executable, *sys.argv])
