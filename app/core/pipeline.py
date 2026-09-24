"""Integração com o pipeline labsin-dados-publicos-am.

Dois modos, decididos pela pasta configurada:
- **Leitor:** só existe o `manifest.json` (por exemplo numa pasta compartilhada). O app mostra
  catálogo, estados e arquivos, mas não consegue coletar.
- **Completo:** a pasta é o próprio pipeline (com `main.py` e um ambiente virtual). O app também
  executa `main.py rodar ...` como processo à parte e acompanha os eventos JSON dele.

O contrato entre os dois é o `manifest.json` (ver src/manifesto.py no pipeline).
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

MANIFEST_SCHEMA = 1
MANIFEST_REL = Path("data") / "poc" / "manifest.json"

# Estado do manifesto -> estado do badge dos cards (ver dataset_card.STATUS_LABELS).
STATE_TO_BADGE = {"nunca": "unchecked", "ok": "updated", "falhou": "error"}


def find_python(folder: Path) -> Path | None:
    """Python do ambiente virtual do pipeline, se existir."""
    exe = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    for venv in ("venv", ".venv"):
        candidate = folder / venv / exe
        if candidate.exists():
            return candidate
    return None


def can_run(folder_text: str) -> bool:
    """True se a pasta é um pipeline executável (main.py + ambiente virtual)."""
    if not folder_text:
        return False
    folder = Path(folder_text)
    return (folder / "main.py").exists() and find_python(folder) is not None


def read_manifest(folder_text: str) -> dict | None:
    """Lê o manifesto da pasta do pipeline. None se não existir ou for de outra versão."""
    if not folder_text:
        return None
    try:
        data = json.loads((Path(folder_text) / MANIFEST_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if data.get("schema_version") == MANIFEST_SCHEMA else None


def _fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB".replace(".", ",")
    return f"{n / (1024 * 1024):.1f} MB".replace(".", ",")


def local_datetime(iso_utc: str) -> datetime | None:
    """Converte '2026-09-23T22:37:00Z' (UTC) para a hora local; None se o texto for inválido."""
    try:
        moment = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None
    return moment.astimezone()


def local_time(iso_utc: str) -> str:
    moment = local_datetime(iso_utc)
    return moment.strftime("%d/%m/%Y %H:%M") if moment else (iso_utc or "—")


def manifest_to_collects(manifest: dict) -> list[dict]:
    """Converte a última execução de cada dataset no formato dos cards da tela de Downloads."""
    collects = []
    for data in manifest.get("datasets", {}).values():
        run = data.get("ultima_execucao")
        if not run or not run.get("arquivos"):
            continue
        files = run["arquivos"]
        by_kind = {"fact": 0, "dim": 0}
        rows = {"fact": 0, "dim": 0}
        for f in files:
            kind = "dim" if f["tabela"].startswith("dim_") else "fact"
            by_kind[kind] += 1
            rows[kind] += f["linhas"]
        collects.append((run["iniciada_em"], {
            "title": data.get("titulo") or data["fonte"],
            "source": data["fonte"],
            "when": local_time(run["iniciada_em"]),
            "trigger": "Coleta manual",
            "versions": [],  # o pipeline ainda não guarda histórico
            "files": [
                (f["arquivo"], _fmt_size(f["tamanho_bytes"]), f"{_fmt_int(f['linhas'])} linhas",
                 "dim" if f["tabela"].startswith("dim_") else "fact")
                for f in files
            ],
            "total_fact": _fmt_int(rows["fact"]) if by_kind["fact"] else "—",
            "total_dim": _fmt_int(rows["dim"]) if by_kind["dim"] else "—",
            "total_size": _fmt_size(sum(f["tamanho_bytes"] for f in files)),
        }))
    # Mais recentes primeiro. Ordena pelo texto ISO original, já que dd/mm/aaaa não ordena.
    collects.sort(key=lambda pair: pair[0], reverse=True)
    return [collect for _, collect in collects]


class PipelineWorker(QThread):
    """Executa `main.py <args>` no pipeline e repassa cada linha JSON como evento."""

    event = Signal(dict)
    failed = Signal(str)

    def __init__(self, folder: Path, args: list[str], parent=None):
        super().__init__(parent)
        self._folder = folder
        self._args = args
        self._process: subprocess.Popen | None = None

    def run(self) -> None:
        python = find_python(self._folder)
        if python is None:
            self.failed.emit("Ambiente virtual do pipeline não encontrado.")
            return
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            self._process = subprocess.Popen(
                [str(python), "main.py", *self._args, "--json"],
                cwd=self._folder, env=env, creationflags=flags,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
            )
        except OSError as exc:
            self.failed.emit(str(exc))
            return

        for line in self._process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self.event.emit(json.loads(line))
            except ValueError:
                pass  # linha que não é JSON (ex.: aviso de biblioteca): ignora
        stderr = self._process.stderr.read()
        code = self._process.wait()
        if code != 0:
            # a última linha do erro costuma ser a mensagem útil ("Erro: ...")
            self.failed.emit(next((l for l in reversed(stderr.splitlines() + [""]) if l.strip()), "")
                             or f"O pipeline terminou com código {code}.")

    def stop(self) -> None:
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()


class PipelineService(QObject):
    """Ponto único de acesso ao pipeline para a interface."""

    catalog_loaded = Signal(dict, bool)      # manifesto/catalogo, pode_executar
    dataset_started = Signal(str)
    dataset_finished = Signal(str, dict)     # nome, evento "fim"
    failed = Signal(str)
    busy_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folder_text = ""
        self._worker: PipelineWorker | None = None

    @property
    def folder(self) -> str:
        return self._folder_text

    @property
    def busy(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    def configure(self, folder_text: str) -> None:
        self._folder_text = folder_text.strip()

    def can_run(self) -> bool:
        return can_run(self._folder_text)

    def refresh(self) -> None:
        """Carrega o catálogo: pelo pipeline (completo) ou só pelo manifesto (leitor)."""
        if self.busy:
            return
        if not self._folder_text:
            return
        if not self.can_run():
            manifest = read_manifest(self._folder_text)
            if manifest is None:
                self.failed.emit("Manifesto do pipeline não encontrado nessa pasta.")
            else:
                self.catalog_loaded.emit(manifest, False)
            return
        self._start(["rodar", "--listar"], on_event=self._on_catalog_event)

    def run(self, names: list[str]) -> None:
        if self.busy or not self.can_run():
            return
        self._start(["rodar", *names], on_event=self._on_run_event)

    def shutdown(self) -> None:
        """Encerra o processo em andamento (ao fechar o app)."""
        if self._worker is not None and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(5000)

    # --- interno -------------------------------------------------------------

    def _start(self, args: list[str], on_event) -> None:
        self._worker = PipelineWorker(Path(self._folder_text), args)
        self._worker.event.connect(on_event)
        self._worker.failed.connect(self.failed)
        self._worker.finished.connect(lambda: self.busy_changed.emit(False))
        self.busy_changed.emit(True)
        self._worker.start()

    def _on_catalog_event(self, event: dict) -> None:
        if event.get("evento") == "catalogo":
            self.catalog_loaded.emit(event, True)

    def _on_run_event(self, event: dict) -> None:
        if event.get("evento") == "inicio":
            self.dataset_started.emit(event["dataset"])
        elif event.get("evento") == "fim":
            self.dataset_finished.emit(event["dataset"], event)
