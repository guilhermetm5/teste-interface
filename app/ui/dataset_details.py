from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.pipeline import STATE_TO_BADGE, fmt_int, fmt_size, local_time
from app.ui.dataset_card import STATUS_LABELS
from app.ui.home_page import hline
from app.ui.updates_page import clear_layout, make_empty_state, make_icon_button, make_label

NO_SELECTION_MESSAGE = "Selecione um dataset para ver os detalhes."


def _wrapped(text: str, name: str, **props) -> QLabel:
    label = make_label(text, name, **props)
    label.setWordWrap(True)
    return label


class DatasetDetails(QWidget):
    """Informações de um dataset: como é coletado, o que gera e como foi a última coleta.

    Recebe um item do manifesto do pipeline (`datasets[nome]`); None mostra o estado vazio.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardsContainer")  # fundo transparente (estilo global), herda o do card
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        self.set_dataset(None)

    def set_dataset(self, data: dict | None) -> None:
        clear_layout(self._layout)
        if data is None:
            self._layout.addWidget(make_empty_state(NO_SELECTION_MESSAGE))
            self._layout.addStretch()
            return

        # Cabeçalho: título, fonte e estado
        self._layout.addWidget(_wrapped(data.get("titulo") or "Dataset", "datasetTitle"))
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(make_label(data["fonte"], "datasetSubtitle"))
        state = STATE_TO_BADGE.get(data["estado"], "unchecked")
        head.addWidget(make_label(STATUS_LABELS[state], "statusBadge", state=state))
        head.addStretch()
        self._layout.addLayout(head)
        self._layout.addWidget(hline())

        # Como é coletado
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        for r, (label, value) in enumerate([
            ("Tipo de coleta", data["tipo_coleta"]),
            ("Periodicidade", data["periodicidade"]),
            ("Granularidade", data["granularidade"]),
        ]):
            grid.addWidget(make_label(label, "metricLabel"), r, 0, Qt.AlignTop)
            grid.addWidget(_wrapped(value, "rowValue"), r, 1)
        grid.setColumnStretch(1, 1)
        self._layout.addLayout(grid)
        self._layout.addWidget(hline())

        # Descrição
        self._layout.addWidget(make_label("Descrição", "panelSection"))
        self._layout.addWidget(_wrapped(data["descricao"], "metricLabel"))

        # Tabelas geradas
        self._layout.addWidget(make_label("Tabelas geradas", "panelSection"))
        for table in data["tabelas_saida"]:
            self._layout.addWidget(make_label(f"{table}.csv", "rowValue"))
        self._layout.addWidget(hline())

        # Última coleta
        self._layout.addWidget(make_label("Última coleta", "panelSection"))
        self._layout.addLayout(self._last_run(data.get("ultima_execucao")))

        url = data.get("url_oficial")
        if url:
            link = make_icon_button("Abrir fonte oficial →", "linkButton")
            link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            self._layout.addWidget(link, 0, Qt.AlignLeft)
        self._layout.addStretch()

    @staticmethod
    def _last_run(run: dict | None) -> QGridLayout | QVBoxLayout:
        if not run:
            box = QVBoxLayout()
            box.addWidget(make_label("Ainda não coletado.", "metricLabel"))
            return box
        files = run["arquivos"]
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        rows = [("Data", local_time(run["iniciada_em"])),
                ("Duração", f"{run['duracao_s']:.1f} s".replace(".", ","))]
        if files:
            rows += [
                ("Arquivos", f"{len(files)}"),
                ("Linhas", fmt_int(sum(f["linhas"] for f in files))),
                ("Tamanho", fmt_size(sum(f["tamanho_bytes"] for f in files))),
            ]
        for r, (label, value) in enumerate(rows):
            grid.addWidget(make_label(label, "metricLabel"), r, 0)
            grid.addWidget(make_label(value, "rowValue"), r, 1, Qt.AlignRight)
        if run["erro"]:
            r = len(rows)
            grid.addWidget(make_label("Erro", "metricLabel"), r, 0, Qt.AlignTop)
            grid.addWidget(_wrapped(run["erro"], "metricValue", tone="bad"), r, 1)
        grid.setColumnStretch(1, 1)
        return grid


class DatasetDetailsDialog(QDialog):
    """Os mesmos detalhes num diálogo (para a janela pequena, onde o painel lateral não aparece)."""

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("detailsDialog")
        self.setWindowTitle(data.get("titulo") or "Detalhes do dataset")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(12)
        self.details = DatasetDetails()
        self.details.set_dataset(data)
        layout.addWidget(self.details, 1)

        close = QPushButton("Fechar")
        close.setObjectName("cardActionButton")
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.accept)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(close)
        layout.addLayout(footer)


DETAILS_STYLESHEET = """
QDialog#detailsDialog { background-color: #212830; }
QFrame#datasetCard[selected="true"] { border: 1px solid #2ebd85; }
"""
