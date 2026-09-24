from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Grupos usados pelas abas: chave -> texto da aba.
TABS = [
    ("available", "Atualizações disponíveis"),
    ("invalid", "Com registros inválidos"),
    ("unchanged", "Sem alteração"),
]

# O pipeline ainda não informa "há versão nova" para as fontes coletáveis, então não há dados reais
# aqui. Cada item, quando existir, tem o formato lido por UpdateRow/DetailPanel (title, source,
# state, badge, group, last_check, last_collect, prev_period, new_period, added, removed, changed,
# valid/valid_pct, errors/errors_pct, empty/empty_pct, rows_prev/rows_now, errs_prev/errs_now,
# note, files, log). `state` reaproveita as cores do QLabel#statusBadge.
NO_UPDATES_MESSAGE = (
    "Nenhuma verificação de atualização disponível. "
    "O pipeline ainda não informa versões novas das fontes."
)

def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def signed(n: int) -> str:
    if n > 0:
        return f"+{fmt(n)}"
    if n < 0:
        return f"-{fmt(-n)}"
    return "0"


def make_label(text: str, name: str, **props) -> QLabel:
    label = QLabel(text)
    label.setObjectName(name)
    for key, value in props.items():
        label.setProperty(key, value)
    return label


def make_empty_state(text: str) -> QLabel:
    """Mensagem centralizada para listas sem dados (em vez de dados de exemplo)."""
    label = make_label(text, "emptyState")
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    return label


def make_icon_button(text: str, name: str, icon: str = "") -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(name)
    button.setCursor(Qt.PointingHandCursor)
    if icon:
        button.setIcon(QIcon(str(PROJECT_ROOT / icon)))
        button.setIconSize(QSize(14, 14))
    return button


def repolish(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def clear_layout(layout) -> None:
    while (item := layout.takeAt(0)) is not None:
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)  # sai da tela já; deleteLater libera a memória depois
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())  # layouts aninhados também têm widgets a apagar


class StatCard(QFrame):
    """Card de resumo no topo: ícone + número, rótulo e observação."""

    def __init__(self, glyph: str, value: int, label: str, sub: str, tone: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setProperty("tone", tone)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(10)
        icon = make_label(glyph, "statIcon", tone=tone)
        icon.setFixedSize(38, 38)
        icon.setAlignment(Qt.AlignCenter)
        top.addWidget(icon)
        top.addWidget(make_label(str(value), "statValue", tone=tone))
        top.addStretch()
        layout.addLayout(top)

        layout.addWidget(make_label(label, "statLabel"))
        layout.addWidget(make_label(sub, "statSub"))


class UpdateRow(QFrame):
    """Linha de dataset. O clique alterna a expansão e seleciona o dataset."""

    clicked = Signal(object)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("updateRow")
        self.setProperty("selected", False)
        self.setCursor(Qt.PointingHandCursor)
        self.data = data
        self.expanded = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())
        self.body = self._build_body()
        self.body.setVisible(False)
        layout.addWidget(self.body)

    def _build_header(self) -> QWidget:
        d = self.data
        header = QWidget()
        h = QHBoxLayout(header)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(12)

        icon = QLabel()
        icon.setObjectName("datasetIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QIcon(str(PROJECT_ROOT / "dataset.png")).pixmap(QSize(24, 24)))
        h.addWidget(icon, 0, Qt.AlignTop)

        info = QVBoxLayout()
        info.setSpacing(3)
        info.addWidget(make_label(d["title"], "datasetTitle"))
        info.addWidget(make_label(d["source"], "datasetSubtitle"))
        info.addWidget(make_label(d["badge"], "statusBadge", state=d["state"]), 0, Qt.AlignLeft)
        h.addLayout(info, 1)

        for caption, value in (("Última verificação", d["last_check"]), ("Última coleta", d["last_collect"])):
            block = QVBoxLayout()
            block.setSpacing(2)
            block.addWidget(make_label(caption, "rowCaption"))
            block.addWidget(make_label(value, "rowValue"))
            h.addLayout(block)

        self.chevron = make_label("›", "chevron")
        h.addWidget(self.chevron)
        return header

    def _build_body(self) -> QWidget:
        d = self.data
        body = QFrame()
        body.setObjectName("rowBody")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        columns.addLayout(self._metrics("ALTERAÇÕES", [
            ("ok", signed(d["added"]).lstrip("+"), "Novos registros"),
            ("bad", fmt(d["removed"]), "Registros removidos"),
            ("ok", fmt(d["changed"]), "Registros alterados"),
        ]))
        columns.addWidget(self._vline())
        columns.addLayout(self._metrics("QUALIDADE", [
            ("ok", fmt(d["valid"]), "Registros válidos"),
            ("bad", fmt(d["errors"]), "Registros com erro"),
            ("warn", fmt(d["empty"]), "Campos vazios"),
        ]))
        columns.addWidget(self._vline())
        columns.addLayout(self._comparison(), 1)
        layout.addLayout(columns)

        footer = QHBoxLayout()
        footer.setSpacing(8)
        footer.addWidget(make_label("ⓘ", "noteIcon"))
        footer.addWidget(make_label(d["note"], "noteText"))
        footer.addStretch()
        self.details_button = make_icon_button("  Ver detalhes", "cardActionButton", "info.png")
        footer.addWidget(self.details_button)
        self.collect_button = make_icon_button("  Coletar dados", "primaryButton", "download.png")
        footer.addWidget(self.collect_button)
        layout.addLayout(footer)
        return body

    @staticmethod
    def _vline() -> QFrame:
        line = QFrame()
        line.setObjectName("separator")
        line.setFrameShape(QFrame.VLine)
        line.setFixedWidth(1)
        return line

    @staticmethod
    def _metrics(title: str, rows: list) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(make_label(title, "columnTitle"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        for r, (tone, value, label) in enumerate(rows):
            grid.addWidget(make_label("●", "dot", tone=tone), r, 0)
            grid.addWidget(make_label(value, "metricValue", tone=tone), r, 1)
            grid.addWidget(make_label(label, "metricLabel"), r, 2)
        grid.setColumnStretch(3, 1)
        col.addLayout(grid)
        col.addStretch()
        return col

    def _comparison(self) -> QVBoxLayout:
        d = self.data
        col = QVBoxLayout()
        col.setSpacing(6)
        col.addWidget(make_label("COMPARAÇÃO  (anterior → atual)", "columnTitle"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(6)
        for c, text in enumerate(("Anterior", "Atual")):
            grid.addWidget(make_label(text, "metricLabel"), 0, c + 1, Qt.AlignRight)
        rows = [
            ("Registros", d["rows_prev"], d["rows_now"], "ok"),
            ("Erros", d["errs_prev"], d["errs_now"], "bad"),
        ]
        for r, (label, prev, now, tone) in enumerate(rows, start=1):
            diff = now - prev
            grid.addWidget(make_label(label, "metricLabel"), r, 0)
            grid.addWidget(make_label(fmt(prev), "rowValue"), r, 1, Qt.AlignRight)
            grid.addWidget(make_label(fmt(now), "metricValue", tone=tone if diff else "muted"), r, 2, Qt.AlignRight)
            grid.addWidget(make_label(signed(diff), "metricValue", tone=tone if diff else "muted"), r, 3, Qt.AlignRight)
        grid.setColumnStretch(0, 1)
        col.addLayout(grid)
        col.addStretch()
        return col

    def set_expanded(self, expanded: bool) -> None:
        self.expanded = expanded
        self.body.setVisible(expanded)
        self.chevron.setText("˄" if expanded else "›")
        self.setProperty("selected", expanded)
        repolish(self)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        super().mousePressEvent(event)


class DetailPanel(QFrame):
    """Painel à direita com o resumo do dataset selecionado."""

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
        icon = QLabel()
        icon.setObjectName("datasetIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QIcon(str(PROJECT_ROOT / "dataset.png")).pixmap(QSize(24, 24)))
        head.addWidget(icon, 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        self.title = make_label("", "datasetTitle")
        self.source = make_label("", "datasetSubtitle")
        titles.addWidget(self.title)
        titles.addWidget(self.source)
        head.addLayout(titles, 1)
        self.close_button = make_icon_button("", "cardButton", "x.png")
        self.close_button.clicked.connect(self.hide)
        head.addWidget(self.close_button, 0, Qt.AlignTop)
        layout.addLayout(head)

        self.badge = make_label("", "statusBadge", state="unchecked")
        layout.addWidget(self.badge, 0, Qt.AlignLeft)
        layout.addWidget(self._hline())

        # Resumo da atualização
        layout.addWidget(make_label("Resumo da atualização", "panelSection"))
        self.summary = {}
        grid = QGridLayout()
        grid.setVerticalSpacing(6)
        for r, (key, label, tone) in enumerate([
            ("prev_period", "Período anterior", ""),
            ("new_period", "Período disponível", ""),
            ("added", "Novos registros", "ok"),
            ("removed", "Registros removidos", "bad"),
            ("changed", "Registros alterados", ""),
        ]):
            grid.addWidget(make_label(label, "metricLabel"), r, 0)
            value = make_label("", "metricValue", tone=tone or "muted")
            grid.addWidget(value, r, 1, Qt.AlignRight)
            self.summary[key] = value
        grid.setColumnStretch(0, 1)
        layout.addLayout(grid)
        layout.addWidget(self._hline())

        # Qualidade dos dados
        layout.addWidget(make_label("Qualidade dos dados", "panelSection"))
        self.quality = {}
        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        for r, (key, label, tone) in enumerate([
            ("valid", "Registros válidos", "ok"),
            ("errors", "Registros com erro", "bad"),
            ("empty", "Campos vazios", "warn"),
        ]):
            grid.addWidget(make_label("●", "dot", tone=tone), r, 0)
            grid.addWidget(make_label(label, "metricLabel"), r, 1)
            value = make_label("", "metricValue", tone=tone)
            pct = make_label("", "metricLabel")
            grid.addWidget(value, r, 2, Qt.AlignRight)
            grid.addWidget(pct, r, 3, Qt.AlignRight)
            self.quality[key] = (value, pct)
        grid.setColumnStretch(1, 1)
        layout.addLayout(grid)
        layout.addWidget(self._hline())

        # Arquivos afetados
        layout.addWidget(make_label("Arquivos que serão atualizados", "panelSection"))
        self.files_layout = QVBoxLayout()
        self.files_layout.setSpacing(6)
        layout.addLayout(self.files_layout)
        layout.addWidget(self._hline())

        # Verificação recente
        log_head = QHBoxLayout()
        log_head.addWidget(make_label("◷  Verificação recente", "panelSection"))
        log_head.addStretch()
        self.run_button = make_icon_button("Ver execução", "cardActionButton")
        log_head.addWidget(self.run_button)
        layout.addLayout(log_head)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("logView")
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(150)
        layout.addWidget(self.log_view)

        self.collect_button = make_icon_button("  Coletar nova versão", "primaryButton", "download.png")
        layout.addWidget(self.collect_button)
        layout.addStretch()

    @staticmethod
    def _hline() -> QFrame:
        line = QFrame()
        line.setObjectName("separator")
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        return line

    def set_dataset(self, d: dict | None) -> None:
        if d is None:  # nenhum dataset selecionado
            d = {"title": "Nenhum dataset selecionado", "source": "", "badge": "", "state": "unchecked",
                 "prev_period": "—", "new_period": "—", "added": 0, "removed": 0, "changed": 0,
                 "valid": 0, "valid_pct": "—", "errors": 0, "errors_pct": "—", "empty": 0,
                 "empty_pct": "—", "files": [], "group": "unchanged", "log": ""}
        self.title.setText(d["title"])
        self.source.setText(d["source"])
        self.badge.setVisible(bool(d["badge"]))
        self.badge.setText(d["badge"])
        self.badge.setProperty("state", d["state"])
        repolish(self.badge)

        self.summary["prev_period"].setText(d["prev_period"])
        self.summary["new_period"].setText(d["new_period"])
        self.summary["added"].setText(signed(d["added"]))
        self.summary["removed"].setText(f"-{fmt(d['removed'])}" if d["removed"] else "0")
        self.summary["changed"].setText(signed(d["changed"]))

        for key, pct_key in (("valid", "valid_pct"), ("errors", "errors_pct"), ("empty", "empty_pct")):
            value, pct = self.quality[key]
            value.setText(fmt(d[key]))
            pct.setText(f"({d[pct_key]})")

        clear_layout(self.files_layout)
        if not d["files"]:
            self.files_layout.addWidget(make_label("Nenhum arquivo será alterado.", "metricLabel"))
        for name, lines, size in d["files"]:
            item = QFrame()
            item.setObjectName("fileItem")
            h = QHBoxLayout(item)
            h.setContentsMargins(10, 8, 10, 8)
            h.setSpacing(10)
            h.addWidget(make_label("CSV", "fileBadge"))
            names = QVBoxLayout()
            names.setSpacing(0)
            names.addWidget(make_label(name, "rowValue"))
            names.addWidget(make_label(lines, "datasetSubtitle"))
            h.addLayout(names, 1)
            h.addWidget(make_label(size, "metricLabel"), 0, Qt.AlignBottom)
            self.files_layout.addWidget(item)

        self.log_view.setPlainText(d.get("log", ""))
        self.collect_button.setEnabled(d["group"] != "unchanged")


class UpdatesPage(QWidget):
    def __init__(self, datasets: list | None = None, parent=None):
        super().__init__(parent)
        datasets = datasets or []
        # Mesma grade da CatalogoPage: o painel de detalhes ocupa a coluna 1 inteira.
        root = QGridLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setHorizontalSpacing(16)
        root.setVerticalSpacing(8)
        root.setColumnStretch(0, 1)
        root.setRowStretch(1, 1)

        header = QVBoxLayout()
        header.setSpacing(8)
        header.addWidget(make_label("Atualizações", "pageTitle"))
        header.addWidget(make_label(
            "Veja o que mudou nos dados e o que precisa ser coletado novamente.", "pageSubtitle"
        ))
        root.addLayout(header, 0, 0)

        body = QVBoxLayout()
        body.setSpacing(12)
        root.addLayout(body, 1, 0)

        self.detail_panel = DetailPanel()
        self.detail_panel.setVisible(False)
        root.addWidget(self.detail_panel, 0, 1, 2, 1)

        counts = {key: sum(1 for d in datasets if d["group"] == key) for key, _ in TABS}

        # Cards de resumo
        stats = QHBoxLayout()
        stats.setSpacing(10)
        last_check = f"Última verificação: {datasets[0]['last_check']}" if datasets else "Nenhuma verificação ainda"
        stats.addWidget(StatCard("▤", len(datasets), "Datasets verificados", last_check, "info"))
        stats.addWidget(StatCard("↑", counts["available"], "Atualizações disponíveis",
                                 "(novos dados)", "ok"))
        stats.addWidget(StatCard("!", counts["invalid"], "Com registros inválidos",
                                 "(precisa de atenção)", "warn"))
        stats.addWidget(StatCard("✓", counts["unchanged"], "Sem alteração",
                                 "(dados atuais)", "muted"))
        body.addLayout(stats)

        # Abas
        tabs = QHBoxLayout()
        tabs.setSpacing(8)
        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)
        self._tab_keys = {}
        for key, label in TABS:
            button = QPushButton(f"{label}   {counts[key]}")
            button.setObjectName("tabButton")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda _c, k=key: self._show_group(k))
            self._tab_group.addButton(button)
            self._tab_keys[key] = button
            tabs.addWidget(button, 1)
        body.addLayout(tabs)

        # Lista de datasets
        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        container.setObjectName("cardsContainer")
        rows_layout = QVBoxLayout(container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(8)

        self.rows = []
        for data in datasets:
            row = UpdateRow(data)
            row.clicked.connect(self._on_row_clicked)
            row.collect_button.clicked.connect(lambda: None)
            rows_layout.addWidget(row)
            self.rows.append(row)
        if not datasets:
            rows_layout.addWidget(make_empty_state(NO_UPDATES_MESSAGE))
        rows_layout.addStretch()
        scroll.setWidget(container)
        body.addWidget(scroll, 1)

        self._tab_keys["available"].setChecked(True)
        self._show_group("available")

    def _show_group(self, group: str) -> None:
        for row in self.rows:
            row.setVisible(row.data["group"] == group)
        selected = next((r for r in self.rows if r.expanded and r.isVisibleTo(self)), None)
        if selected is None:
            selected = next((r for r in self.rows if r.data["group"] == group), None)
        self._select(selected)

    def _select(self, selected) -> None:
        for row in self.rows:
            row.set_expanded(row is selected)
        self.detail_panel.set_dataset(selected.data if selected is not None else None)

    def _on_row_clicked(self, row: UpdateRow) -> None:
        if row.expanded:
            row.set_expanded(False)
        else:
            self._select(row)


UPDATES_STYLESHEET = """
QLabel#emptyState {
    color: #9aa5b1;
    font-size: 13px;
    padding: 32px;
    border: 1px dashed #3a4552;
    border-radius: 8px;
}
QFrame#statCard {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 8px;
}
QFrame#statCard[tone="info"] { background-color: #1c2a3a; border: 1px solid #2f4a68; }
QFrame#statCard[tone="ok"]   { background-color: #17302a; border: 1px solid #22574a; }
QFrame#statCard[tone="warn"] { background-color: #2f2a1a; border: 1px solid #5a4a20; }
QLabel#statIcon {
    border-radius: 19px;
    font-size: 18px;
    font-weight: bold;
}
QLabel#statIcon[tone="info"]  { background-color: #2b4a6e; color: #8fc1f0; }
QLabel#statIcon[tone="ok"]    { background-color: #1f6b52; color: #7ee0b4; }
QLabel#statIcon[tone="warn"]  { background-color: #6b5220; color: #f0b95a; }
QLabel#statIcon[tone="muted"] { background-color: #34404d; color: #c4ccd4; }
QLabel#statValue { font-size: 24px; font-weight: bold; color: #d6dbe0; }
QLabel#statValue[tone="info"] { color: #8fc1f0; }
QLabel#statValue[tone="ok"]   { color: #6fd39b; }
QLabel#statValue[tone="warn"] { color: #f0b95a; }
QLabel#statLabel { color: #d6dbe0; font-size: 12px; }
QLabel#statSub   { color: #9aa5b1; font-size: 11px; }

QPushButton#tabButton {
    background-color: transparent;
    color: #d6dbe0;
    border: 1px solid #3a4552;
    border-radius: 6px;
    padding: 10px 12px;
}
QPushButton#tabButton:hover { background-color: #2b3440; }
QPushButton#tabButton:checked {
    background-color: #17302a;
    border: 1px solid #2ebd85;
    color: #ffffff;
    font-weight: bold;
}

QFrame#updateRow {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 8px;
}
QFrame#updateRow:hover { border: 1px solid #4a5868; }
QFrame#updateRow[selected="true"] { border: 1px solid #2ebd85; }
QFrame#rowBody { background: transparent; border: none; border-top: 1px solid #3a4552; }
QLabel#rowCaption { color: #9aa5b1; font-size: 11px; }
QLabel#rowValue   { color: #d6dbe0; font-size: 12px; }
QLabel#chevron    { color: #9aa5b1; font-size: 18px; }
QLabel#columnTitle { color: #9aa5b1; font-size: 11px; font-weight: bold; }
QLabel#metricLabel { color: #9aa5b1; font-size: 12px; }
QLabel#metricValue { font-size: 14px; font-weight: bold; color: #d6dbe0; }
QLabel#metricValue[tone="ok"]    { color: #6fd39b; }
QLabel#metricValue[tone="bad"]   { color: #f08a8a; }
QLabel#metricValue[tone="warn"]  { color: #f0b95a; }
QLabel#metricValue[tone="muted"] { color: #d6dbe0; }
QLabel#dot { font-size: 10px; }
QLabel#dot[tone="ok"]   { color: #6fd39b; }
QLabel#dot[tone="bad"]  { color: #f08a8a; }
QLabel#dot[tone="warn"] { color: #f0b95a; }
QLabel#noteIcon { color: #9aa5b1; font-size: 14px; }
QLabel#noteText { color: #9aa5b1; font-size: 12px; }

QPushButton#primaryButton {
    background-color: #2ebd85;
    color: #0e2a1f;
    border: none;
    border-radius: 4px;
    padding: 8px 14px;
    font-weight: bold;
}
QPushButton#primaryButton:hover    { background-color: #3ccd94; }
QPushButton#primaryButton:pressed  { background-color: #27a374; }
QPushButton#primaryButton:disabled { background-color: #2b3440; color: #6d7a87; }

QFrame#detailPanel {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 8px;
}
QLabel#panelSection { color: #ffffff; font-size: 13px; font-weight: bold; }
QFrame#fileItem {
    background-color: #212830;
    border: 1px solid #3a4552;
    border-radius: 6px;
}
QLabel#fileBadge {
    background-color: #1f4d36;
    color: #6fd39b;
    border-radius: 4px;
    padding: 6px 4px;
    font-size: 10px;
    font-weight: bold;
}
QPlainTextEdit#logView {
    background-color: #12171c;
    color: #c4ccd4;
    border: 1px solid #3a4552;
    border-radius: 6px;
    font-family: Consolas, monospace;
    font-size: 11px;
    padding: 6px;
}
"""
