from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.updates_page import StatCard, make_icon_button, make_label

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GREEN = "#2ebd85"
BLUE = "#3a8ee6"
PURPLE = "#7a5ccf"
ORANGE = "#e8833a"
TEAL = "#22b8b0"
GREY = "#7a879a"
AMBER = "#f0b95a"
RED = "#e05c5c"
TEXT = "#d6dbe0"

# Dados de exemplo (layout apenas). `state` reaproveita as cores do QLabel#statusBadge.
RECENT_COLLECTS = [
    ("População dos municípios", "IBGE · API", "Concluída", "updated", "23/09/2026 10:24", "63.248 linhas"),
    ("Saúde por município", "DATASUS · API", "Concluída", "updated", "23/09/2026 09:42", "98.421 linhas"),
    ("Educação básica", "INEP · API", "Com erros", "update_available", "22/09/2026 16:37", "45.882 linhas"),
    ("PIB municipal", "IBGE · API", "Atualizando", "processing", "22/09/2026 14:12", "62.100 linhas"),
    ("Desmatamento", "INPE · API", "Pendente", "unchecked", "21/09/2026 09:51", "31.772 linhas"),
]

DATASET_STATUS = [
    ("Atualizados", GREEN, 18, "75%"),
    ("Com atualização", AMBER, 3, "12%"),
    ("Com erro", RED, 1, "4%"),
    ("Sem dados", GREY, 2, "8%"),
]

ACTIVITY = [
    ("10:24", "ok", "População dos municípios", "2 arquivos gerados (fato + dimensão)"),
    ("09:42", "ok", "Saúde por município", "2 arquivos gerados (fato + dimensão)"),
    ("Ontem\n16:37", "bad", "Educação básica", "18 registros com erro"),
    ("Ontem\n14:12", "warn", "PIB municipal", "Nova versão detectada"),
    ("Ontem\n09:51", "muted", "Desmatamento", "Verificação concluída"),
]

THEME_ACTIVITY = [
    ("População", 4, GREEN),
    ("Saúde", 3, BLUE),
    ("Educação", 2, PURPLE),
    ("Economia", 1, ORANGE),
    ("Meio Ambiente", 1, TEAL),
    ("Outros", 1, GREY),
]


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


class BarChart(QWidget):
    """Gráfico de barras simples: valor acima da barra e rótulo embaixo."""

    def __init__(self, data: list, parent=None):
        super().__init__(parent)
        self.data = data
        self.setMinimumHeight(150)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont(self.font())
        font.setPixelSize(11)
        painter.setFont(font)

        label_h, value_h = 18, 18
        chart_h = self.height() - label_h - value_h
        slot = self.width() / len(self.data)
        bar_w = min(slot * 0.55, 44)
        top = max(value for _, value, _ in self.data)

        for i, (label, value, color) in enumerate(self.data):
            x = i * slot + (slot - bar_w) / 2
            bar_h = max(6, chart_h * value / top)
            y = value_h + chart_h - bar_h
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(QRectF(x, y, bar_w, bar_h), 3, 3)

            painter.setPen(QColor(TEXT))
            painter.drawText(QRectF(i * slot, y - value_h, slot, value_h), Qt.AlignCenter, str(value))
            painter.setPen(QColor("#9aa5b1"))
            painter.drawText(QRectF(i * slot, self.height() - label_h, slot, label_h), Qt.AlignCenter, label)


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
        body = QVBoxLayout(content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)
        root.addWidget(scroll, 1, 0)

        body.addLayout(self._build_stats())
        body.addWidget(self._build_alert())
        panels = QGridLayout()
        panels.setHorizontalSpacing(12)
        panels.setVerticalSpacing(12)
        panels.setColumnStretch(0, 3)
        panels.setColumnStretch(1, 2)
        panels.addWidget(self._build_collects(), 0, 0)
        panels.addWidget(self._build_status(), 0, 1)
        panels.addWidget(self._build_themes(), 1, 0)
        panels.addWidget(self._build_activity(), 1, 1)
        body.addLayout(panels)
        body.addStretch()

        # Coluna lateral: só aparece com a janela maximizada (controlado pela MainWindow).
        self.side_column = QWidget()
        self.side_column.setFixedWidth(320)
        self.side_column.setVisible(False)
        side = QVBoxLayout(self.side_column)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        side.addWidget(self._build_quick_actions())
        side.addWidget(self._build_highlights())
        side.addStretch()
        root.addWidget(self.side_column, 0, 1, 2, 1)

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
        stamp.addWidget(make_label("Última atualização da plataforma", "rowCaption"))
        stamp.addWidget(make_label("23/09/2026 10:24", "rowValue"))
        h.addLayout(stamp)
        return h

    def _build_stats(self) -> QHBoxLayout:
        stats = QHBoxLayout()
        stats.setSpacing(10)
        stats.addWidget(StatCard("▤", 24, "Datasets disponíveis", "Fontes de dados do Amazonas", "info"))
        stats.addWidget(StatCard("↻", 3, "Atualizações pendentes", "Datasets com novos dados", "warn"))
        stats.addWidget(StatCard("▶", 12, "Coletas realizadas", "Últimos 7 dias", "ok"))
        stats.addWidget(StatCard("↓", 47, "Arquivos gerados", "CSV, atualizações e histórico", "purple"))
        return stats

    def _build_alert(self) -> QFrame:
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
        texts.addWidget(make_label("3 datasets possuem novos dados disponíveis", "panelTitle"))
        texts.addWidget(make_label(
            "Verifique as atualizações para coletar a nova versão dos dados.", "datasetSubtitle"
        ))
        h.addLayout(texts, 1)
        self.alert_button = QPushButton("→  Ver atualizações")
        self.alert_button.setObjectName("alertButton")
        self.alert_button.setCursor(Qt.PointingHandCursor)
        self.alert_button.clicked.connect(lambda: self.navigate.emit("update"))
        h.addWidget(self.alert_button)
        return banner

    def _build_collects(self) -> Panel:
        panel = Panel("◷", "Últimas coletas", "Coletas mais recentes realizadas no sistema", "Ver todas →")
        panel.link_button.clicked.connect(lambda: self.navigate.emit("download"))
        panel.body.setSpacing(0)
        for i, (title, source, status, state, when, lines) in enumerate(RECENT_COLLECTS):
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
            info.addWidget(make_label(title, "rowValue"))
            info.addWidget(make_label(source, "datasetSubtitle"))
            h.addLayout(info, 1)
            h.addWidget(make_label(status, "statusBadge", state=state))
            when_box = QVBoxLayout()
            when_box.setSpacing(1)
            when_box.addWidget(make_label(when, "rowValue"))
            when_box.addWidget(make_label(lines, "datasetSubtitle"))
            h.addLayout(when_box)
            h.addWidget(make_label("›", "chevron"))
            panel.body.addWidget(row)
        return panel

    def _build_status(self) -> Panel:
        panel = Panel("▥", "Status dos datasets", "Visão geral da situação atual")
        h = QHBoxLayout()
        h.setSpacing(14)
        chart = DonutChart([(color, count) for _, color, count, _ in DATASET_STATUS], "24", "total")
        h.addWidget(chart)
        legend = QGridLayout()
        legend.setHorizontalSpacing(8)
        legend.setVerticalSpacing(8)
        for r, (label, color, count, pct) in enumerate(DATASET_STATUS):
            dot = make_label("●", "legendDot")
            dot.setStyleSheet(f"color: {color};")
            legend.addWidget(dot, r, 0)
            legend.addWidget(make_label(label, "metricLabel"), r, 1)
            legend.addWidget(make_label(f"{count} ({pct})", "metricLabel"), r, 2, Qt.AlignRight)
        legend.setColumnStretch(1, 1)
        h.addLayout(legend, 1)
        panel.body.addLayout(h)
        return panel

    def _build_themes(self) -> Panel:
        panel = Panel("▥", "Atividade por tema", "Distribuição das coletas nos últimos 7 dias")
        panel.body.addWidget(BarChart(THEME_ACTIVITY))
        return panel

    def _build_activity(self) -> Panel:
        panel = Panel("ϟ", "Atividade recente", "Últimas ações no sistema")
        for when, tone, title, desc in ACTIVITY:
            h = QHBoxLayout()
            h.setSpacing(10)
            time_label = make_label(when, "metricLabel")
            time_label.setFixedWidth(42)
            h.addWidget(time_label, 0, Qt.AlignTop)
            h.addWidget(make_label("●", "dot", tone=tone), 0, Qt.AlignTop)
            texts = QVBoxLayout()
            texts.setSpacing(0)
            texts.addWidget(make_label(title, "rowValue"))
            texts.addWidget(make_label(desc, "datasetSubtitle"))
            h.addLayout(texts, 1)
            panel.body.addLayout(h)
        link = QPushButton("Ver todas as atividades →")
        link.setObjectName("linkButton")
        link.setCursor(Qt.PointingHandCursor)
        link.clicked.connect(lambda: self.navigate.emit("update"))
        panel.body.addWidget(link, 0, Qt.AlignRight)
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

    def _build_highlights(self) -> Panel:
        panel = Panel("☆", "Destaques", "")

        def item(glyph, tone, title, sub):
            h = QHBoxLayout()
            h.setSpacing(10)
            icon = make_label(glyph, "statIcon", tone=tone)
            icon.setFixedSize(30, 30)
            icon.setAlignment(Qt.AlignCenter)
            h.addWidget(icon, 0, Qt.AlignTop)
            texts = QVBoxLayout()
            texts.setSpacing(1)
            texts.addWidget(make_label(title, "rowValue"))
            texts.addWidget(make_label(sub, "datasetSubtitle"))
            h.addLayout(texts, 1)
            return h, texts

        row, _ = item("!", "ok", "Sistema funcionando normalmente", "Todos os serviços operacionais")
        panel.body.addLayout(row)
        panel.body.addWidget(hline())
        row, _ = item("i", "info", "Próxima verificação", "23/09/2026 16:00")
        panel.body.addLayout(row)
        panel.body.addWidget(hline())
        row, texts = item("▤", "muted", "Espaço em disco (arquivos)", "42,7 GB de 100 GB (43%)")
        bar = QProgressBar()
        bar.setObjectName("diskBar")
        bar.setRange(0, 100)
        bar.setValue(43)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        texts.addWidget(bar)
        panel.body.addLayout(row)
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

QProgressBar#diskBar {
    background-color: #2b3440;
    border: none;
    border-radius: 3px;
}
QProgressBar#diskBar::chunk {
    background-color: #2ebd85;
    border-radius: 3px;
}
"""
