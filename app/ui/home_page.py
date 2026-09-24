from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core.pipeline import local_datetime, local_time
from app.ui.updates_page import StatCard, clear_layout, make_empty_state, make_label

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GREEN = "#2ebd85"
GREY = "#7a879a"
RED = "#e05c5c"


class DonutChart(QWidget):
    """Gráfico de rosca com o total no centro."""

    def __init__(self, segments: list, total_text: str, caption: str, parent=None):
        super().__init__(parent)
        self.segments = segments
        self.total_text = total_text
        self.caption = caption
        self.setFixedSize(124, 124)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        thickness = 14
        rect = QRectF(thickness, thickness, self.width() - 2 * thickness, self.height() - 2 * thickness)

        total = sum(value for _, value in self.segments) or 1
        start = 90 * 16
        for color, value in self.segments:
            span = -int(value / total * 360 * 16)
            painter.setPen(QPen(QColor(color), thickness, Qt.SolidLine, Qt.FlatCap))
            painter.drawArc(rect, start, span)
            start += span

        painter.setPen(QColor("#ffffff"))
        font = QFont(self.font())
        font.setPixelSize(22)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, self.height() / 2 - 20, self.width(), 26), Qt.AlignCenter, self.total_text)

        painter.setPen(QColor("#9aa5b1"))
        font.setPixelSize(11)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(QRectF(0, self.height() / 2 + 4, self.width(), 16), Qt.AlignCenter, self.caption)


class Panel(QFrame):
    """Card com cabeçalho (ícone, título, subtítulo, link opcional) e um corpo vazio."""

    def __init__(self, glyph: str, title: str, subtitle: str, link: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("homePanel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(make_label(glyph, "panelGlyph"), 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(1)
        titles.addWidget(make_label(title, "panelTitle"))
        if subtitle:
            titles.addWidget(make_label(subtitle, "datasetSubtitle"))
        head.addLayout(titles, 1)
        self.link_button = None
        if link:
            self.link_button = QPushButton(link)
            self.link_button.setObjectName("linkButton")
            self.link_button.setCursor(Qt.PointingHandCursor)
            head.addWidget(self.link_button, 0, Qt.AlignTop)
        outer.addLayout(head)

        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body)
        # Sem isso, a altura extra da grade seria repartida com o cabeçalho.
        outer.addStretch(1)


class ActionCard(QFrame):
    """Cartão clicável das ações rápidas."""

    clicked = Signal()

    def __init__(self, glyph: str, title: str, subtitle: str, tone: str, parent=None):
        super().__init__(parent)
        self.setObjectName("actionCard")
        self.setProperty("tone", tone)
        self.setCursor(Qt.PointingHandCursor)

        h = QHBoxLayout(self)
        h.setContentsMargins(12, 10, 12, 10)
        h.setSpacing(12)
        icon = make_label(glyph, "statIcon", tone=tone)
        icon.setFixedSize(38, 38)
        icon.setAlignment(Qt.AlignCenter)
        h.addWidget(icon)
        texts = QVBoxLayout()
        texts.setSpacing(1)
        texts.addWidget(make_label(title, "actionTitle", tone=tone))
        texts.addWidget(make_label(subtitle, "datasetSubtitle"))
        h.addLayout(texts, 1)
        h.addWidget(make_label("→", "chevron"))

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


def hline() -> QFrame:
    line = QFrame()
    line.setObjectName("separator")
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    return line


class HomePage(QWidget):
    # Pede ao app para abrir outra página, pelo id do item da sidebar.
    navigate = Signal(str)
    # Pede à MainWindow para baixar e instalar a atualização do aplicativo.
    update_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QGridLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setHorizontalSpacing(16)
        root.setVerticalSpacing(12)
        root.setColumnStretch(0, 1)
        root.setRowStretch(1, 1)

        root.addLayout(self._build_header(), 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setObjectName("cardsContainer")
        scroll.setWidget(content)
        # Tudo que depende de dados fica aqui dentro e é refeito em set_manifest().
        self.body = QVBoxLayout(content)
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(12)
        root.addWidget(scroll, 1, 0)

        # Coluna lateral: só aparece com a janela maximizada (controlado pela MainWindow).
        self.side_column = QWidget()
        self.side_column.setFixedWidth(320)
        self.side_column.setVisible(False)
        side = QVBoxLayout(self.side_column)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        side.addWidget(self._build_quick_actions())
        side.addStretch()
        root.addWidget(self.side_column, 0, 1, 2, 1)

        self.set_manifest(None)

    # --- dados ----------------------------------------------------------------

    def set_manifest(self, manifest: dict | None) -> None:
        """Refaz os blocos com os dados do manifesto do pipeline (None = sem dados)."""
        clear_layout(self.body)
        datasets = list((manifest or {}).get("datasets", {}).values())
        runs = sorted(
            (d for d in datasets if d.get("ultima_execucao")),
            key=lambda d: d["ultima_execucao"]["iniciada_em"], reverse=True,
        )
        generated = local_time(manifest["gerado_em"]) if manifest and manifest.get("gerado_em") else "—"
        self.stamp_value.setText(generated)

        self.body.addLayout(self._build_stats(datasets, runs))
        failed = [d for d in datasets if d["estado"] == "falhou"]
        if failed:
            self.body.addWidget(self._build_alert(len(failed)))
        panels = QGridLayout()
        panels.setHorizontalSpacing(12)
        panels.setVerticalSpacing(12)
        panels.setColumnStretch(0, 3)
        panels.setColumnStretch(1, 2)
        panels.addWidget(self._build_collects(runs), 0, 0)
        panels.addWidget(self._build_status(datasets), 0, 1)
        panels.addWidget(self._build_activity(runs), 1, 0, 1, 2)
        self.body.addLayout(panels)
        self.body.addStretch()

    # --- blocos ---------------------------------------------------------------

    def _build_header(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(12)
        icon = QLabel()
        icon.setObjectName("datasetIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QIcon(str(PROJECT_ROOT / "home.png")).pixmap(QSize(24, 24)))
        h.addWidget(icon, 0, Qt.AlignTop)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(make_label("Início", "pageTitle"))
        titles.addWidget(make_label("Visão geral da coleta de dados do Amazonas", "pageSubtitle"))
        h.addLayout(titles, 1)

        h.addWidget(make_label("▦", "panelGlyph"), 0, Qt.AlignTop)
        stamp = QVBoxLayout()
        stamp.setSpacing(1)
        stamp.addWidget(make_label("Última geração dos dados", "rowCaption"))
        self.stamp_value = make_label("—", "rowValue")
        stamp.addWidget(self.stamp_value)
        h.addLayout(stamp)

        # Só aparece quando o app detecta uma versão nova (ver set_update_available).
        self.update_button = QPushButton("↑  Atualizar agora")
        self.update_button.setObjectName("updateNowButton")
        self.update_button.setCursor(Qt.PointingHandCursor)
        self.update_button.setVisible(False)
        self.update_button.clicked.connect(self.update_requested)
        h.addWidget(self.update_button, 0, Qt.AlignVCenter)
        return h

    def set_update_available(self, available: bool) -> None:
        self.update_button.setVisible(available)

    def set_update_busy(self, busy: bool) -> None:
        self.update_button.setEnabled(not busy)
        self.update_button.setText("Atualizando..." if busy else "↑  Atualizar agora")

    def _build_stats(self, datasets: list, runs: list) -> QHBoxLayout:
        never = sum(1 for d in datasets if d["estado"] == "nunca")
        files = sum(len(d["ultima_execucao"]["arquivos"]) for d in runs)
        stats = QHBoxLayout()
        stats.setSpacing(10)
        stats.addWidget(StatCard("▤", len(datasets), "Datasets disponíveis", "Fontes do pipeline", "info"))
        stats.addWidget(StatCard("↻", never, "Ainda não coletados", "Datasets sem nenhuma coleta", "warn"))
        stats.addWidget(StatCard("▶", len(runs), "Coletas realizadas", "Última de cada dataset", "ok"))
        stats.addWidget(StatCard("↓", files, "Arquivos gerados", "CSVs da última coleta", "purple"))
        return stats

    def _build_alert(self, failed: int) -> QFrame:
        banner = QFrame()
        banner.setObjectName("alertBanner")
        h = QHBoxLayout(banner)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(12)
        icon = make_label("!", "statIcon", tone="warn")
        icon.setFixedSize(34, 34)
        icon.setAlignment(Qt.AlignCenter)
        h.addWidget(icon)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        plural = "datasets falharam" if failed != 1 else "dataset falhou"
        texts.addWidget(make_label(f"{failed} {plural} na última coleta", "panelTitle"))
        texts.addWidget(make_label("Veja o motivo em Explorar dados e tente coletar de novo.", "datasetSubtitle"))
        h.addLayout(texts, 1)
        button = QPushButton("→  Explorar dados")
        button.setObjectName("alertButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda: self.navigate.emit("explore"))
        h.addWidget(button)
        return banner

    def _build_collects(self, runs: list) -> Panel:
        panel = Panel("◷", "Últimas coletas", "Coletas mais recentes realizadas no sistema", "Ver todas →")
        panel.link_button.clicked.connect(lambda: self.navigate.emit("download"))
        panel.body.setSpacing(0)
        if not runs:
            panel.body.addWidget(make_empty_state("Nenhuma coleta realizada ainda."))
            return panel
        for i, d in enumerate(runs[:5]):
            run = d["ultima_execucao"]
            failed = bool(run["erro"])
            lines = sum(f["linhas"] for f in run["arquivos"])
            if i:
                panel.body.addWidget(hline())
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 8, 0, 8)
            h.setSpacing(12)
            icon = QLabel()
            icon.setObjectName("datasetIcon")
            icon.setFixedSize(36, 36)
            icon.setAlignment(Qt.AlignCenter)
            icon.setPixmap(QIcon(str(PROJECT_ROOT / "dataset.png")).pixmap(QSize(20, 20)))
            h.addWidget(icon)
            info = QVBoxLayout()
            info.setSpacing(1)
            info.addWidget(make_label(d.get("titulo") or d["fonte"], "rowValue"))
            info.addWidget(make_label(d["fonte"], "datasetSubtitle"))
            h.addLayout(info, 1)
            h.addWidget(make_label("Falhou" if failed else "Concluída", "statusBadge",
                                   state="error" if failed else "updated"))
            when = QVBoxLayout()
            when.setSpacing(1)
            when.addWidget(make_label(local_time(run["iniciada_em"]), "rowValue"))
            when.addWidget(make_label("sem arquivos" if failed else f"{lines:,} linhas".replace(",", "."),
                                      "datasetSubtitle"))
            h.addLayout(when)
            panel.body.addWidget(row)
        return panel

    def _build_status(self, datasets: list) -> Panel:
        panel = Panel("▥", "Status dos datasets", "Situação da última coleta")
        if not datasets:
            panel.body.addWidget(make_empty_state("Sem datasets para mostrar."))
            return panel
        legend_rows = [
            ("Coletados", GREEN, sum(1 for d in datasets if d["estado"] == "ok")),
            ("Com erro", RED, sum(1 for d in datasets if d["estado"] == "falhou")),
            ("Sem coleta", GREY, sum(1 for d in datasets if d["estado"] == "nunca")),
        ]
        total = len(datasets)
        h = QHBoxLayout()
        h.setSpacing(14)
        h.addWidget(DonutChart([(color, n) for _, color, n in legend_rows], str(total), "total"))
        legend = QGridLayout()
        legend.setHorizontalSpacing(8)
        legend.setVerticalSpacing(8)
        for r, (label, color, n) in enumerate(legend_rows):
            dot = make_label("●", "legendDot")
            dot.setStyleSheet(f"color: {color};")
            legend.addWidget(dot, r, 0)
            legend.addWidget(make_label(label, "metricLabel"), r, 1)
            legend.addWidget(make_label(f"{n} ({round(100 * n / total)}%)", "metricLabel"), r, 2, Qt.AlignRight)
        legend.setColumnStretch(1, 1)
        h.addLayout(legend, 1)
        panel.body.addLayout(h)
        return panel

    def _build_activity(self, runs: list) -> Panel:
        panel = Panel("ϟ", "Atividade recente", "Últimas ações no sistema")
        if not runs:
            panel.body.addWidget(make_empty_state("Nenhuma atividade registrada ainda."))
            return panel
        today = datetime.now().astimezone().date()
        for d in runs[:5]:
            run = d["ultima_execucao"]
            moment = local_datetime(run["iniciada_em"])
            if moment is None:
                when = "—"
            elif moment.date() == today:
                when = moment.strftime("%H:%M")
            else:
                when = moment.strftime("%d/%m\n%H:%M")
            failed = bool(run["erro"])
            n = len(run["arquivos"])
            desc = f"Erro: {run['erro']}" if failed else f"{n} arquivo{'s' if n != 1 else ''} gerado{'s' if n != 1 else ''}"
            h = QHBoxLayout()
            h.setSpacing(10)
            time_label = make_label(when, "metricLabel")
            time_label.setFixedWidth(42)
            h.addWidget(time_label, 0, Qt.AlignTop)
            h.addWidget(make_label("●", "dot", tone="bad" if failed else "ok"), 0, Qt.AlignTop)
            texts = QVBoxLayout()
            texts.setSpacing(0)
            texts.addWidget(make_label(d.get("titulo") or d["fonte"], "rowValue"))
            detail = make_label(desc, "datasetSubtitle")
            detail.setWordWrap(True)
            texts.addWidget(detail)
            h.addLayout(texts, 1)
            panel.body.addLayout(h)
        return panel

    def _build_quick_actions(self) -> Panel:
        panel = Panel("ϟ", "Ações rápidas", "Acesse as principais funções do sistema")
        for glyph, title, sub, tone, target in [
            ("⌕", "Explorar dados", "Buscar e descobrir datasets", "info", "explore"),
            ("↻", "Ver atualizações", "Ver o que mudou nos datasets", "ok", "update"),
            ("↓", "Downloads", "Acessar arquivos gerados", "purple", "download"),
        ]:
            card = ActionCard(glyph, title, sub, tone)
            card.clicked.connect(lambda t=target: self.navigate.emit(t))
            panel.body.addWidget(card)
        return panel


HOME_STYLESHEET = """
QFrame#statCard[tone="purple"] { background-color: #241f3d; border: 1px solid #453a78; }
QLabel#statIcon[tone="purple"] { background-color: #43377a; color: #b9a6f5; }
QLabel#statValue[tone="purple"] { color: #b9a6f5; }

QFrame#homePanel {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 8px;
}
QLabel#panelGlyph { color: #9aa5b1; font-size: 18px; }
QLabel#panelTitle { color: #ffffff; font-size: 13px; font-weight: bold; }
QLabel#legendDot { font-size: 12px; }
QLabel#dot[tone="info"]  { color: #7fb8ea; }
QLabel#dot[tone="muted"] { color: #7a879a; }

QPushButton#linkButton {
    background: transparent;
    border: none;
    color: #5aa9f5;
    font-size: 12px;
    padding: 2px 4px;
}
QPushButton#linkButton:hover { color: #8cc4fa; }

QPushButton#updateNowButton {
    background-color: #3a6ea5;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 14px;
    font-weight: bold;
}
QPushButton#updateNowButton:hover    { background-color: #4a7fb8; }
QPushButton#updateNowButton:pressed  { background-color: #2f5c8a; }
QPushButton#updateNowButton:disabled { background-color: #2b3440; color: #6d7a87; }

QFrame#alertBanner {
    background-color: #2f2a1a;
    border: 1px solid #5a4a20;
    border-radius: 8px;
}
QPushButton#alertButton {
    background-color: #5a4318;
    color: #f0b95a;
    border: 1px solid #7a5f24;
    border-radius: 4px;
    padding: 8px 14px;
}
QPushButton#alertButton:hover { background-color: #6b5220; }

QFrame#actionCard { border-radius: 8px; }
QFrame#actionCard[tone="info"] { background-color: #14305c; border: 1px solid #1f5aa8; }
QFrame#actionCard[tone="ok"]   { background-color: #17302a; border: 1px solid #22574a; }
QFrame#actionCard[tone="purple"] { background-color: #241f3d; border: 1px solid #453a78; }
QFrame#actionCard:hover { border-width: 2px; }
QLabel#actionTitle { font-size: 13px; }
QLabel#actionTitle[tone="info"]   { color: #8fc1f0; }
QLabel#actionTitle[tone="ok"]     { color: #6fd39b; }
QLabel#actionTitle[tone="purple"] { color: #b9a6f5; }
"""
