import requests
from PySide6.QtCore import QThread, Signal

GITHUB_OWNER = "guilhermetm5"
GITHUB_REPO = "teste-interface"
GITHUB_BRANCH = "main"

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"


def fetch_remote_commit(timeout: float = 5.0) -> dict:
    """Consulta a API pública do GitHub pelo commit mais recente da branch."""
    response = requests.get(
        API_URL,
        timeout=timeout,
        headers={"Accept": "application/vnd.github+json"},
    )
    response.raise_for_status()
    data = response.json()
    return {
        "sha": data["sha"],
        "message": data["commit"]["message"].splitlines()[0],
        "url": data["html_url"],
    }


class UpdateCheckWorker(QThread):
    """Roda a checagem de atualização em background para não travar a UI."""

    finished_ok = Signal(dict)
    finished_error = Signal(str)

    def run(self) -> None:
        try:
            info = fetch_remote_commit()
        except requests.RequestException as exc:
            self.finished_error.emit(str(exc))
            return
        self.finished_ok.emit(info)
