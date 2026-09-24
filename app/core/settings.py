"""Configurações do usuário, salvas fora do projeto em %APPDATA%\\DadosAmazonas\\settings.json.

Ficam fora do repositório para sobreviverem ao `git pull` das atualizações do app.
"""

import copy
import json
import os
import tempfile
from pathlib import Path

SETTINGS_VERSION = 1

DEFAULTS = {
    "version": SETTINGS_VERSION,
    "coleta": {
        "pasta_saida": str(Path.home() / "DadosAmazonas"),
        "pasta_por_dataset": True,
        "registrar_logs": True,
    },
    "verificacao": {
        "verificar_ao_iniciar": True,
        # "avisar" | "perguntar"
        "comportamento": "avisar",
    },
    "arquivos": {
        "codificacao": "utf-8",
        "separador": ";",
        "incluir_origem_dado": True,
        "incluir_data_coleta": True,
        "manter_versoes": True,
    },
}


def settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    return base / "DadosAmazonas" / "settings.json"


def _merge(defaults: dict, stored: dict) -> dict:
    """Completa `stored` com os padrões. Valores de tipo errado voltam ao padrão."""
    result = {}
    for key, default in defaults.items():
        value = stored.get(key, default) if isinstance(stored, dict) else default
        if isinstance(default, dict):
            result[key] = _merge(default, value)
        elif isinstance(value, type(default)):
            result[key] = value
        else:
            result[key] = default
    return result


def load() -> dict:
    """Lê as configurações. Arquivo ausente ou corrompido devolve os padrões."""
    try:
        stored = json.loads(settings_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stored = {}
    settings = _merge(DEFAULTS, stored)
    settings["version"] = SETTINGS_VERSION
    return settings


def save(settings: dict) -> None:
    """Grava as configurações de forma atômica (arquivo temporário + rename)."""
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(_merge(DEFAULTS, settings), ensure_ascii=False, indent=2)

    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix="settings.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            tmp.write(data)
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def defaults() -> dict:
    return copy.deepcopy(DEFAULTS)
