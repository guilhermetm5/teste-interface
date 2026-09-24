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

# Dados de exemplo (layout apenas). `state` reaproveita as cores do QLabel#statusBadge.
DATASETS = [
    {
        "title": "População dos municípios",
        "source": "IBGE · API",
        "state": "update_available",
        "badge": "Nova versão disponível",
        "group": "available",
        "last_check": "23/09/2026 10:24",
        "last_collect": "12/09/2026",
        "prev_period": "2024",
        "new_period": "2025",
        "added": 1248, "removed": 12, "changed": 184,
        "valid": 1230, "valid_pct": "98,4%",
        "errors": 18, "errors_pct": "1,4%",
        "empty": 7, "empty_pct": "0,2%",
        "rows_prev": 62000, "rows_now": 63248,
        "errs_prev": 5, "errs_now": 18,
        "note": "Novos dados disponíveis para o período de 2025.",
        "files": [
            ("fato_populacao.csv", "+1.248 linhas", "~ 8,4 MB"),
            ("dim_municipio.csv", "+0 linhas", "~ 2,1 MB"),
        ],
    },
    {
        "title": "Internações hospitalares",
        "source": "DATASUS · API",
        "state": "update_available",
        "badge": "Atualização disponível",
        "group": "available",
        "last_check": "22/09/2026 16:37",
        "last_collect": "10/08/2026",
        "prev_period": "07/2026",
        "new_period": "08/2026",
        "added": 5310, "removed": 0, "changed": 42,
        "valid": 5300, "valid_pct": "99,8%",
        "errors": 10, "errors_pct": "0,2%",
        "empty": 0, "empty_pct": "0,0%",
        "rows_prev": 91200, "rows_now": 96510,
        "errs_prev": 2, "errs_now": 10,
        "note": "Novos dados disponíveis para agosto de 2026.",
        "files": [("fato_internacoes.csv", "+5.310 linhas", "~ 12,7 MB")],
    },
    {
        "title": "Educação básica",
        "source": "INEP · API",
        "state": "error",
        "badge": "Com registros inválidos",
        "group": "invalid",
        "last_check": "22/09/2026 14:12",
        "last_collect": "05/08/2026",
        "prev_period": "2024",
        "new_period": "2025",
        "added": 830, "removed": 4, "changed": 96,
        "valid": 760, "valid_pct": "91,6%",
        "errors": 62, "errors_pct": "7,5%",
        "empty": 8, "empty_pct": "1,0%",
        "rows_prev": 40100, "rows_now": 40926,
        "errs_prev": 3, "errs_now": 62,
        "note": "Há registros inválidos que precisam de atenção antes da coleta.",
        "files": [("fato_matriculas.csv", "+830 linhas", "~ 3,2 MB")],
    },
    {
        "title": "PIB municipal",
        "source": "IBGE · API",
        "state": "unchecked",
        "badge": "Sem alteração",
        "group": "unchanged",
        "last_check": "22/09/2026 11:03",
        "last_collect": "15/08/2026",
        "prev_period": "2023",
        "new_period": "2023",
        "added": 0, "removed": 0, "changed": 0,
        "valid": 62, "valid_pct": "100%",
        "errors": 0, "errors_pct": "0,0%",
        "empty": 0, "empty_pct": "0,0%",
        "rows_prev": 62, "rows_now": 62,
        "errs_prev": 0, "errs_now": 0,
        "note": "Os dados estão atualizados.",
        "files": [],
    },
    {
        "title": "Desmatamento",
        "source": "INPE · API",
        "state": "unchecked",
        "badge": "Sem alteração",
        "group": "unchanged",
        "last_check": "21/09/2026 09:51",
        "last_collect": "20/08/2026",
        "prev_period": "2025",
        "new_period": "2025",
        "added": 0, "removed": 0, "changed": 0,
        "valid": 1520, "valid_pct": "100%",
        "errors": 0, "errors_pct": "0,0%",
        "empty": 0, "empty_pct": "0,0%",
        "rows_prev": 1520, "rows_now": 1520,
        "errs_prev": 0, "errs_now": 0,
        "note": "Os dados estão atualizados.",
        "files": [],
    },
]

LOG_TIMES = ["10:24:17", "10:24:19", "10:24:20", "10:24:21", "10:24:22", "10:24:22", "10:24:23"]
LOG_RESULT = {
    "available": "NOVOS DADOS ENCONTRADOS",
    "invalid": "REGISTROS INVÁLIDOS ENCONTRADOS",
    "unchanged": "NENHUMA ALTERAÇÃO",
}


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def signed(n: int) -> str:
    if n > 0:
        return f"+{fmt(n)}"
    if n < 0:
        return f"-{fmt(-n)}"
    return "0"


def build_log(d: dict) -> str:
    source = d["source"].split(" · ")[0]
    lines = [
        "Iniciando verificação...",
        f"Conectando à API do {source}...",
        f"Consultando {d['title'].lower()}...",
        f"Último período disponível: {d['new_period']}",
        f"Último período coletado: {d['prev_period']}",
        LOG_RESULT[d["group"]],
        "Verificação concluída.",
    ]
    return "\n".join(f"{t}  {line}" for t, line in zip(LOG_TIMES, lines))


def make_label(text: str, name: str, **props) -> QLabel:
    label = QLabel(text)
    label.setObjectName(name)
    for key, value in props.items():
        label.setProperty(key, value)
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
        if item.widget() is not None:
            item.widget().deleteLater()


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

    def set_dataset(self, d: dict) -> None:
        self.title.setText(d["title"])
        self.source.setText(d["source"])
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

        self.log_view.setPlainText(build_log(d))
        self.collect_button.setEnabled(d["group"] != "unchanged")


class UpdatesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        counts = {key: sum(1 for d in DATASETS if d["group"] == key) for key, _ in TABS}

        # Cards de resumo
        stats = QHBoxLayout()
        stats.setSpacing(10)
        stats.addWidget(StatCard("▤", len(DATASETS), "Datasets verificados",
                                 f"Última verificação: {DATASETS[0]['last_check']}", "info"))
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
        for data in DATASETS:
            row = UpdateRow(data)
            row.clicked.connect(self._on_row_clicked)
            row.collect_button.clicked.connect(lambda: None)
            rows_layout.addWidget(row)
            self.rows.append(row)
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
        if selected is not None:
            self.detail_panel.set_dataset(selected.data)

    def _on_row_clicked(self, row: UpdateRow) -> None:
        if row.expanded:
            row.set_expanded(False)
        else:
            self._select(row)


UPDATES_STYLESHEET = """
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
