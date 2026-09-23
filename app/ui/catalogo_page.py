from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILTER_PLACEHOLDERS = ["Todos os temas", "Todas as fontes", "Todos os formatos", "Última atualização"]

CATALOGO_ITEMS = ["População dos municípios"]


class CatalogoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Dados do Amazonas")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Conecte-se as principais fontes de dados do estado, encontre o que precisa\ne gere seu arquivo CSV de forma simples e rapida.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Buscar por palavra-chave, município, tema ou fonte...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.addAction(
            QIcon(str(PROJECT_ROOT / "lupa.png")), QLineEdit.LeadingPosition
        )
        self.search_input.textChanged.connect(self._filter_items)
        layout.addWidget(self.search_input)

        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(8)

        self.filter_combos = []
        for placeholder in FILTER_PLACEHOLDERS:
            combo = QComboBox()
            combo.setObjectName("filterCombo")
            combo.addItem(placeholder)
            filters_layout.addWidget(combo, 1)
            self.filter_combos.append(combo)

        self.filter_button = QPushButton()
        self.filter_button.setObjectName("filterButton")
        filters_layout.addWidget(self.filter_button)

        layout.addLayout(filters_layout)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("catalogList")
        self.list_widget.addItems(CATALOGO_ITEMS)
        layout.addWidget(self.list_widget)

    def _filter_items(self, text: str) -> None:
        text = text.strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text not in item.text().lower())
