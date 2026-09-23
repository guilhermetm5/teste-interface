from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.animated_combo import AnimatedComboBox
from app.ui.dataset_card import DatasetCard
from app.ui.side_panel import SidePanel

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cada filtro: (texto padrão, opções). O texto padrão é sempre o primeiro item.
FILTERS = [
    (
        "Todos os temas",
        [
            "EDUCAÇÃO",
            "MEIO AMBIENTE",
            "POPULAÇÃO",
            "SANEAMENTO",
            "SAÚDE",
            "SEGURANÇA",
            "SOCIOECONOMICOS",
        ],
    ),
    ("Todas as fontes", []),
    ("Todos os formatos", []),
    ("Última atualização", []),
]

CATALOGO_ITEMS = [
    {
        "title": "População dos municípios",
        "subtitle": "Estimativas populacionais dos municípios do Amazonas.",
        "badges": ["IBGE", "Demografia", "CSV"],
        "has_update": False,
    },
]


class CatalogoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Grade: título/subtítulo na linha 0; o restante e o side panel na linha 1,
        # assim o painel começa alinhado ao campo de busca.
        root_layout = QGridLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setHorizontalSpacing(16)
        root_layout.setVerticalSpacing(8)
        root_layout.setColumnStretch(0, 1)
        root_layout.setRowStretch(1, 1)

        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        root_layout.addLayout(header_layout, 0, 0)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        root_layout.addLayout(layout, 1, 0)

        self.side_panel = SidePanel()
        self.side_panel.setVisible(False)
        root_layout.addWidget(self.side_panel, 1, 1)

        title = QLabel("Dados do Amazonas")
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Conecte-se as principais fontes de dados do estado, encontre o que precisa\ne gere seu arquivo CSV de forma simples e rapida.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

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
        for placeholder, options in FILTERS:
            combo = AnimatedComboBox()
            combo.setObjectName("filterCombo")
            combo.addItem(placeholder)
            combo.addItems(options)
            filters_layout.addWidget(combo, 1)
            self.filter_combos.append(combo)

        self.filter_button = QPushButton("  Limpar")
        self.filter_button.setObjectName("filterButton")
        self.filter_button.setIcon(QIcon(str(PROJECT_ROOT / "x.png")))
        self.filter_button.setIconSize(QSize(14, 14))
        filters_layout.addWidget(self.filter_button)

        layout.addLayout(filters_layout)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        section_title = QLabel("Fontes de dados")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        cards_container = QWidget()
        cards_container.setObjectName("cardsContainer")
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(8)

        self.dataset_cards = []
        for item in CATALOGO_ITEMS:
            card = DatasetCard(**item)
            cards_layout.addWidget(card)
            self.dataset_cards.append(card)
        cards_layout.addStretch()

        scroll.setWidget(cards_container)
        layout.addWidget(scroll, 1)

    def _filter_items(self, text: str) -> None:
        text = text.strip().lower()
        for card in self.dataset_cards:
            card.setVisible(card.matches(text))
