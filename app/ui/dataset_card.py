from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Estados possíveis do dataset -> texto do badge. As cores ficam no QSS
# (QLabel#statusBadge[state="..."] em main_window.py).
STATUS_LABELS = {
    "updated": "Atualizado",
    "update_available": "Atualização disponível",
    "unchecked": "Não verificado",
    "error": "Erro ao baixar/tratar",
    "processing": "Processando",
}


class DatasetCard(QFrame):
    """Card horizontal: ícone | título + subtítulo + badges | status + botões."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        badges: list[str],
        status: str = "unchecked",
        icon: str = "dataset.png",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("datasetCard")
        self.title = title
        self.subtitle = subtitle
        self.badges = badges

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Parte 1: ícone
        icon_label = QLabel()
        icon_label.setObjectName("datasetIcon")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QIcon(str(PROJECT_ROOT / icon)).pixmap(QSize(24, 24)))
        layout.addWidget(icon_label, 0, Qt.AlignTop)

        # Parte 2: título + subtítulo + badges
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("datasetTitle")
        info_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("datasetSubtitle")
        subtitle_label.setWordWrap(True)
        info_layout.addWidget(subtitle_label)

        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(6)
        for text in badges:
            badge = QLabel(text)
            badge.setObjectName("badge")
            badges_layout.addWidget(badge)
        badges_layout.addStretch()
        info_layout.addLayout(badges_layout)

        layout.addLayout(info_layout, 1)

        # Parte 3: status + botões
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusBadge")
        self.set_status(status)
        actions_layout.addWidget(self.status_label, 0, Qt.AlignRight)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.details_button = QPushButton("  Detalhes")
        self.details_button.setObjectName("cardActionButton")
        self.details_button.setIcon(QIcon(str(PROJECT_ROOT / "info.png")))
        self.details_button.setIconSize(QSize(16, 16))
        buttons_layout.addWidget(self.details_button)

        self.source_button = QPushButton("  Ver fonte")
        self.source_button.setObjectName("cardActionButton")
        self.source_button.setIcon(QIcon(str(PROJECT_ROOT / "link.png")))
        self.source_button.setIconSize(QSize(14, 14))
        buttons_layout.addWidget(self.source_button)

        self.download_button = QPushButton("  Baixar")
        self.download_button.setObjectName("cardDownloadButton")
        self.download_button.setIcon(QIcon(str(PROJECT_ROOT / "download.png")))
        self.download_button.setIconSize(QSize(14, 14))
        buttons_layout.addWidget(self.download_button)

        actions_layout.addLayout(buttons_layout)
        layout.addLayout(actions_layout)

    def set_status(self, status: str) -> None:
        """Atualiza o badge de status. `status` é uma chave de STATUS_LABELS."""
        self.status = status
        self.status_label.setText(STATUS_LABELS[status])
        self.status_label.setProperty("state", status)
        # Reaplica o QSS, já que o seletor depende da propriedade dinâmica.
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def matches(self, text: str) -> bool:
        haystack = " ".join([self.title, self.subtitle, *self.badges]).lower()
        return text in haystack
