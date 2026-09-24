from pathlib import Path

from PySide6.QtCore import QSize, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QIcon
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

from app.core.pipeline import STATE_TO_BADGE
from app.ui.animated_combo import AnimatedComboBox
from app.ui.dataset_card import DatasetCard
from app.ui.dataset_details import DatasetDetailsDialog
from app.ui.side_panel import SidePanel
from app.ui.updates_page import clear_layout, make_empty_state

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

NO_PIPELINE_MESSAGE = "Nenhum dataset carregado. Informe a pasta do pipeline em Configurações."


class CatalogoPage(QWidget):
    # Usuário pediu para coletar um dataset do pipeline (nome no catálogo).
    run_requested = Signal(str)

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
        self.cards_layout = QVBoxLayout(cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)

        self.dataset_cards = []
        self.show_empty(NO_PIPELINE_MESSAGE)

        scroll.setWidget(cards_container)
        layout.addWidget(scroll, 1)

    def _show_cards(self, cards: list, empty_text: str = "") -> None:
        clear_layout(self.cards_layout)
        self.dataset_cards = cards
        self._selected_card = None
        self.side_panel.details.set_dataset(None)
        for card in cards:
            self.cards_layout.addWidget(card)
        if not cards:
            self.cards_layout.addWidget(make_empty_state(empty_text or NO_PIPELINE_MESSAGE))
        self.cards_layout.addStretch()
        self._filter_items(self.search_input.text())

    def show_empty(self, text: str) -> None:
        """Sem cards: mostra uma mensagem explicando por quê."""
        self._show_cards([], text)

    def set_pipeline_datasets(self, datasets: dict, can_run: bool) -> None:
        """Mostra os datasets reais do pipeline (nome -> dados do manifesto)."""
        cards = []
        for name, data in datasets.items():
            summary = data["descricao"].split(". ")[0].strip()
            card = DatasetCard(
                title=data.get("titulo") or name,
                subtitle=summary if len(summary) <= 120 else summary[:117] + "...",
                badges=[data["fonte"], data["granularidade"], data["periodicidade"]],
                status=STATE_TO_BADGE.get(data["estado"], "unchecked"),
            )
            card.setToolTip(data["descricao"])
            card.dataset_name = name
            card.dataset_data = data
            card.download_button.setText("  Coletar")
            card.download_button.setEnabled(can_run)
            if not can_run:
                card.download_button.setToolTip("Pipeline não encontrado nesta máquina (modo leitor).")
            card.download_button.clicked.connect(lambda _c=False, n=name: self.run_requested.emit(n))
            card.clicked.connect(self._select)
            card.details_button.clicked.connect(lambda _c=False, c=card: self._show_details(c))
            card.source_button.clicked.connect(lambda _c=False, u=data.get("url_oficial"): self._open_url(u))
            cards.append(card)
        self._show_cards(cards, "O pipeline não tem datasets disponíveis para coletar.")

    def _select(self, card: DatasetCard) -> None:
        """Marca o card e mostra os detalhes dele no painel lateral."""
        self._selected_card = card
        for other in self.dataset_cards:
            other.set_selected(other is card)
        self.side_panel.details.set_dataset(getattr(card, "dataset_data", None))

    def _show_details(self, card: DatasetCard) -> None:
        """Botão "Detalhes": com o painel lateral visível só seleciona; senão abre um diálogo."""
        self._select(card)
        if not self.side_panel.isVisible():
            DatasetDetailsDialog(card.dataset_data, self).exec()

    @staticmethod
    def _open_url(url: str | None) -> None:
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def update_datasets(self, datasets: dict) -> None:
        """Atualiza os dados guardados nos cards (ex.: depois de uma coleta) e o painel de detalhes."""
        for card in self.dataset_cards:
            name = getattr(card, "dataset_name", None)
            if name in datasets:
                card.dataset_data = datasets[name]
                if card is self._selected_card:
                    self.side_panel.details.set_dataset(card.dataset_data)

    def set_dataset_state(self, name: str, badge_state: str, detail: str = "") -> None:
        """Atualiza o badge de um card; `detail` (ex.: mensagem de erro) vira o tooltip do badge."""
        for card in self.dataset_cards:
            if getattr(card, "dataset_name", None) == name:
                card.set_status(badge_state)
                card.status_label.setToolTip(detail)

    def set_collect_enabled(self, enabled: bool) -> None:
        """Habilita ou desabilita os botões "Coletar" (ex.: enquanto uma coleta roda)."""
        for card in self.dataset_cards:
            if hasattr(card, "dataset_name"):
                card.download_button.setEnabled(enabled)

    def _filter_items(self, text: str) -> None:
        text = text.strip().lower()
        for card in self.dataset_cards:
            card.setVisible(card.matches(text))
