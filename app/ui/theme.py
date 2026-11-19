import re
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DARK = "escuro"
LIGHT = "claro"

# Cor do glifo dos ícones (todos são brancos sobre fundo transparente).
ICON_COLORS = {DARK: "#ffffff", LIGHT: "#26303b"}

# O QSS é escrito com as cores do tema escuro; o claro troca cada uma pela equivalente.
_LIGHT_COLORS = {
    "#212830": "#f4f6f8",  # fundo
    "#1a2027": "#e6eaee",  # sidebar e painéis
    "#1f2730": "#eef1f4",
    "#2b3440": "#d5dbe2",  # hover
    "#34404d": "#c8d1da",  # selecionado
    "#3c4956": "#bcc7d2",
    "#3a4552": "#c3ccd6",  # bordas
    "#4a5868": "#a9b5c2",
    "#d6dbe0": "#26303b",  # texto
    "#ffffff": "#0f1720",  # texto forte
    "#9aa5b1": "#5b6773",  # texto secundário
    "#c4ccd4": "#4a5563",
    "#1f4d36": "#d6f0e0", "#6fd39b": "#1f7a46",
    "#5a4318": "#f7e8c6", "#f0b95a": "#8a5a00",
    "#5a2323": "#f6d5d5", "#f08a8a": "#a32a2a",
    "#1f3d5a": "#d3e5f5", "#7fb8ea": "#1f5f9a",
}


def apply_theme(stylesheet: str, theme: str) -> str:
    if theme != LIGHT:
        return stylesheet
    return re.sub(
        r"#[0-9a-fA-F]{6}\b",
        lambda match: _LIGHT_COLORS.get(match.group(0).lower(), match.group(0)),
        stylesheet,
    )


def tinted_icon(filename: str, color: str) -> QIcon:
    """Ícone do projeto com o glifo pintado na cor pedida (mantém a transparência)."""
    pixmap = QPixmap(str(PROJECT_ROOT / filename))
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)
