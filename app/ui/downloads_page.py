from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
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
from app.ui.home_page import hline
from app.ui.updates_page import clear_layout, make_empty_state, make_icon_button, make_label, repolish

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cada arquivo de uma coleta: (nome, tamanho, linhas, tipo "fact"|"dim").
NO_COLLECTS_MESSAGE = "Nenhuma coleta ainda. Colete um dataset em Explorar dados."

FILTER_DEFAULTS = ["Todos os datasets", "Todos os tipos", "Todos os status"]


def dataset_icon(size: int, pixmap: int) -> QLabel:
    icon = QLabel()
    icon.setObjectName("datasetIcon")
    icon.setFixedSize(size, size)
    icon.setAlignment(Qt.AlignCenter)
    icon.setPixmap(QIcon(str(PROJECT_ROOT / "dataset.png")).pixmap(QSize(pixmap, pixmap)))
    return icon


def file_item(name: str, size: str, lines: str, kind: str) -> QWidget:
    row = QWidget()
    h = QHBoxLayout(row)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(8)
    h.addWidget(make_label("CSV", "fileBadge", kind=kind))
    texts = QVBoxLayout()
    texts.setSpacing(0)
    texts.addWidget(make_label(name, "rowValue"))
    texts.addWidget(make_label(f"{size} · {lines}", "datasetSubtitle"))
    h.addLayout(texts, 1)
    return row


class CollectCard(QFrame):
    """Card de uma coleta: dataset | arquivos gerados | conjunto de dados e ações."""

    clicked = Signal(object)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("collectCard")
        self.setProperty("selected", False)
        self.setCursor(Qt.PointingHandCursor)
        self.data = data

        h = QHBoxLayout(self)
        h.setContentsMargins(14, 14, 14, 14)
        h.setSpacing(16)

        # Parte 1: ícone + dataset + status + data
        left = QHBoxLayout()
        left.setSpacing(12)
        left.addWidget(dataset_icon(48, 26), 0, Qt.AlignTop)
        info = QVBoxLayout()
        info.setSpacing(3)
        info.addWidget(make_label(data["title"], "datasetTitle"))
        info.addWidget(make_label(data["source"], "datasetSubtitle"))
        info.addWidget(make_label("Concluído", "statusBadge", state="updated"), 0, Qt.AlignLeft)
        info.addWidget(make_label(f"▦  {data['when']}", "datasetSubtitle"))
        info.addWidget(make_label(f"◔  {data['trigger']}", "datasetSubtitle"))
        left.addLayout(info, 1)
        h.addLayout(left, 3)

        # Parte 2: arquivos gerados
        files = QVBoxLayout()
        files.setSpacing(8)
        files.addWidget(make_label("Arquivos gerados", "rowCaption"))
        for name, size, lines, kind in data["files"]:
            files.addWidget(file_item(name, size, lines, kind))
        files.addStretch()
        h.addLayout(files, 3)

        # Parte 3: conjunto de dados + botões
        right = QVBoxLayout()
        right.setSpacing(4)
        right.addWidget(make_label("Conjunto de dados", "rowCaption"))
        right.addWidget(make_label(data["title"], "rowValue"))
        right.addStretch()
        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        self.folder_button = make_icon_button("Abrir pasta", "cardActionButton")
        self.open_button = make_icon_button("↗  Abrir conjunto", "primaryButton")
        buttons.addWidget(self.folder_button)
        buttons.addWidget(self.open_button)
        right.addLayout(buttons)
        h.addLayout(right, 3)

        h.addWidget(make_label("›", "chevron"), 0, Qt.AlignTop)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        repolish(self)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)


class CollectDetailPanel(QFrame):
    """Painel à direita com o resumo da coleta selecionada."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailPanel")
        self.setFixedWidth(340)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("cardsContainer")
        scroll.setWidget(content)
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Cabeçalho
        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(dataset_icon(48, 26), 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.title = make_label("", "datasetTitle")
        self.source = make_label("", "datasetSubtitle")
        self.badge = make_label("Concluído", "statusBadge", state="updated")
        titles.addWidget(self.title)
        titles.addWidget(self.source)
        titles.addWidget(self.badge, 0, Qt.AlignLeft)
        head.addLayout(titles, 1)
        self.close_button = make_icon_button("", "cardButton", "x.png")
        self.close_button.clicked.connect(self.hide)
        head.addWidget(self.close_button, 0, Qt.AlignTop)
        layout.addLayout(head)

        self.when = make_label("", "metricLabel")
        self.trigger = make_label("", "metricLabel")
        layout.addWidget(self.when)
        layout.addWidget(self.trigger)
        layout.addWidget(hline())

        # Resumo da coleta
        layout.addWidget(make_label("Resumo da coleta", "panelSection"))
        self.summary = {}
        grid = QGridLayout()
        grid.setVerticalSpacing(6)
        for r, (key, label) in enumerate([
            ("datasets", "Datasets"),
            ("total_fact", "Total de registros (fato)"),
            ("total_dim", "Total de registros (dimensão)"),
            ("total_size", "Tamanho total"),
        ]):
            grid.addWidget(make_label(label, "metricLabel"), r, 0)
            value = make_label("", "metricValue", tone="muted")
            grid.addWidget(value, r, 1, Qt.AlignRight)
            self.summary[key] = value
        grid.setColumnStretch(0, 1)
        layout.addLayout(grid)
        layout.addWidget(hline())

        # Arquivos gerados
        layout.addWidget(make_label("Arquivos gerados", "panelSection"))
        self.files_layout = QVBoxLayout()
        self.files_layout.setSpacing(6)
        layout.addLayout(self.files_layout)
        layout.addWidget(hline())

        # Versões anteriores
        layout.addWidget(make_label("◷  Versões anteriores", "panelSection"))
        self.versions_box = QVBoxLayout()  # preenchido em set_collect()
        layout.addLayout(self.versions_box)
        self.history_button = QPushButton("Ver histórico completo →")
        self.history_button.setObjectName("linkButton")
        self.history_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.history_button, 0, Qt.AlignLeft)
        layout.addWidget(hline())

        # Ações rápidas
        layout.addWidget(make_label("Ações rápidas", "panelSection"))
        self.folder_button = make_icon_button("Abrir pasta", "cardActionButton")
        self.open_button = make_icon_button("Abrir conjunto", "cardActionButton")
        self.delete_button = make_icon_button("Excluir coleta", "dangerButton")
        for button in (self.folder_button, self.open_button, self.delete_button):
            layout.addWidget(button)
        layout.addStretch()

    def _set_versions(self, versions: list) -> None:
        """Lista de versões anteriores (data, linhas, tamanho). Vazia = ainda não há histórico."""
        clear_layout(self.versions_box)
        if not versions:
            note = make_label("Sem versões anteriores: o pipeline ainda não guarda o histórico.", "datasetSubtitle")
            note.setWordWrap(True)
            self.versions_box.addWidget(note)
            self.history_button.setVisible(False)
            return
        self.history_button.setVisible(True)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        for r, (date, lines, size) in enumerate(versions):
            grid.addWidget(make_label(date, "rowValue"), r, 0)
            grid.addWidget(make_label(lines, "metricLabel"), r, 1, Qt.AlignRight)
            grid.addWidget(make_label(size, "metricLabel"), r, 2, Qt.AlignRight)
        grid.setColumnStretch(1, 1)
        self.versions_box.addLayout(grid)

    def set_collect(self, d: dict | None) -> None:
        if d is None:  # nenhuma coleta selecionada
            d = {"title": "Nenhuma coleta selecionada", "source": "", "when": "", "trigger": "",
                 "files": [], "total_fact": "—", "total_dim": "—", "total_size": "—", "versions": []}
        self.title.setText(d["title"])
        self.source.setText(d["source"])
        self.when.setText(f"▦  {d['when']}" if d["when"] else "")
        self.trigger.setText(f"◔  {d['trigger']}" if d["trigger"] else "")
        n = len(d["files"])
        self.summary["datasets"].setText(f"{n} arquivo{'s' if n != 1 else ''}")
        for key in ("total_fact", "total_dim", "total_size"):
            self.summary[key].setText(d[key])

        self._set_versions(d.get("versions", []))

        clear_layout(self.files_layout)
        for name, size, lines, kind in d["files"]:
            item = QFrame()
            item.setObjectName("fileItem")
            h = QHBoxLayout(item)
            h.setContentsMargins(10, 8, 10, 8)
            h.setSpacing(8)
            h.addWidget(file_item(name, size, lines, kind), 1)
            h.addWidget(make_icon_button("", "cardButton", "download.png"))
            h.addWidget(make_label("⋮", "chevron"))
            self.files_layout.addWidget(item)


class DownloadsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QGridLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setHorizontalSpacing(16)
        root.setVerticalSpacing(12)
        root.setColumnStretch(0, 1)
        root.setRowStretch(1, 1)

        root.addLayout(self._build_header(), 0, 0)

        body = QVBoxLayout()
        body.setSpacing(12)
        root.addLayout(body, 1, 0)

        self.detail_panel = CollectDetailPanel()
        self.detail_panel.setVisible(False)
        root.addWidget(self.detail_panel, 0, 1, 2, 1)

        # Busca + filtros
        filters = QHBoxLayout()
        filters.setSpacing(10)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Buscar por dataset, arquivo ou data...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.addAction(QIcon(str(PROJECT_ROOT / "lupa.png")), QLineEdit.LeadingPosition)
        self.search_input.textChanged.connect(self._apply_filters)
        filters.addWidget(self.search_input, 3)

        self.filter_combos = []
        for i, default in enumerate(FILTER_DEFAULTS):
            combo = AnimatedComboBox()
            combo.setObjectName("filterCombo")
            combo.addItem(default)
            if i == 0:
                combo.currentIndexChanged.connect(self._apply_filters)  # opções: set_collects()
            elif i == 1:
                combo.addItem("CSV")
            else:
                combo.addItem("Concluído")
            filters.addWidget(combo, 1)
            self.filter_combos.append(combo)
        body.addLayout(filters)

        # Título da lista + ordenação
        head = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(make_label("Coletas recentes", "sectionTitle"))
        self.results_label = make_label("", "pageSubtitle")
        titles.addWidget(self.results_label)
        head.addLayout(titles, 1)
        self.sort_combo = AnimatedComboBox()
        self.sort_combo.setObjectName("filterCombo")
        self.sort_combo.addItems(["Mais recentes", "Mais antigas"])
        head.addWidget(self.sort_combo, 0, Qt.AlignBottom)
        body.addLayout(head)

        # Lista de coletas
        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container.setObjectName("cardsContainer")
        self.cards_layout = QVBoxLayout(container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards = []
        scroll.setWidget(container)
        body.addWidget(scroll, 1)

        self.set_collects([])

    def set_collects(self, collects: list) -> None:
        """Substitui a lista de coletas (exemplo ou reais, vindas do manifesto do pipeline)."""
        clear_layout(self.cards_layout)
        self.cards = []
        for data in collects:
            card = CollectCard(data)
            card.clicked.connect(self._select)
            self.cards_layout.addWidget(card)
            self.cards.append(card)
        if not collects:
            self.cards_layout.addWidget(make_empty_state(NO_COLLECTS_MESSAGE))
        self.cards_layout.addStretch()

        # O filtro de datasets acompanha os títulos que existem agora.
        combo = self.filter_combos[0]
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(FILTER_DEFAULTS[0])
        combo.addItems(sorted({c["title"] for c in collects}))
        combo.blockSignals(False)

        self._apply_filters()
        if self.cards:
            self._select(self.cards[0])
        else:
            self.detail_panel.set_collect(None)

    def _build_header(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(12)
        icon = QLabel()
        icon.setObjectName("datasetIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QIcon(str(PROJECT_ROOT / "download.png")).pixmap(QSize(24, 24)))
        h.addWidget(icon, 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(make_label("Downloads", "pageTitle"))
        titles.addWidget(make_label("Acesse os arquivos gerados nas coletas dos seus datasets.", "pageSubtitle"))
        h.addLayout(titles, 1)
        return h

    def _apply_filters(self) -> None:
        text = self.search_input.text().strip().lower()
        dataset = self.filter_combos[0].currentText() if self.filter_combos[0].currentIndex() > 0 else ""
        visible = 0
        for card in self.cards:
            d = card.data
            haystack = " ".join([d["title"], d["when"], *(f[0] for f in d["files"])]).lower()
            show = text in haystack and (not dataset or d["title"] == dataset)
            card.setVisible(show)
            visible += show
        self.results_label.setText(f"{visible} resultado{'s' if visible != 1 else ''}")

    def _select(self, selected: CollectCard) -> None:
        for card in self.cards:
            card.set_selected(card is selected)
        self.detail_panel.set_collect(selected.data)


DOWNLOADS_STYLESHEET = """
QFrame#collectCard {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 8px;
}
QFrame#collectCard:hover { border: 1px solid #4a5868; }
QFrame#collectCard[selected="true"] { border: 1px solid #2ebd85; }

QLabel#fileBadge[kind="dim"] {
    background-color: #1f3f66;
    color: #7fb8ea;
}

QPushButton#dangerButton {
    background-color: transparent;
    color: #f08a8a;
    border: 1px solid #a53b3b;
    border-radius: 4px;
    padding: 8px 14px;
}
QPushButton#dangerButton:hover   { background-color: #3a1f1f; }
QPushButton#dangerButton:pressed { background-color: #4a2727; }
"""
