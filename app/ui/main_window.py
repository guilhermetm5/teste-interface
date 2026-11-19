from pathlib import Path

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core import settings
from app.ui.frameless import (
    RESIZE_MARGIN,
    TITLE_BAR_HEIGHT,
    TITLE_BAR_STYLESHEET,
    ResizableContainer,
    TitleBar,
)
from app.ui.sidebar import Sidebar
from app.ui.theme import DARK, ICON_COLORS, LIGHT, apply_theme

STYLESHEET = """
QMainWindow {
    background: transparent;
}
QWidget#content {
    background-color: #212830;
}
QFrame#sidebar {
    background-color: #1a2027;
    border-bottom-left-radius: 6px;
}
QPushButton#sidebarButton {
    color: #d6dbe0;
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 8px 12px;
    border-radius: 4px;
}
QPushButton#sidebarButton:hover {
    background-color: #2b3440;
}
QPushButton#sidebarButton:pressed {
    background-color: #34404d;
}
QPushButton#sidebarButton:checked {
    background-color: #34404d;
    color: #ffffff;
}
QPushButton#sidebarButton:checked:hover {
    background-color: #3c4956;
}
QPushButton#sidebarButton:focus {
    outline: none;
}
QLabel#contentLabel {
    color: #d6dbe0;
    font-size: 16px;
}
QLabel#pageTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}
QLineEdit#searchInput {
    background-color: #1a2027;
    color: #d6dbe0;
    border: 1px solid #3a4552;
    border-radius: 4px;
    padding: 8px 12px;
}
QLineEdit#searchInput:focus {
    border: 1px solid #3a6ea5;
}
QComboBox#filterCombo {
    background-color: #1a2027;
    color: #d6dbe0;
    border: 1px solid #3a4552;
    border-radius: 4px;
    padding: 8px 12px;
}
QComboBox#filterCombo:hover {
    border: 1px solid #4a5868;
}
QComboBox#filterCombo::drop-down {
    border: none;
    background: transparent;
    width: 24px;
}
QComboBox#filterCombo::down-arrow {
    image: url(ARROW_DOWN_PATH);
    width: 12px;
    height: 12px;
}
QComboBox#filterCombo QAbstractItemView {
    background-color: #212830;
    color: #d6dbe0;
    selection-background-color: #34404d;
    border: 1px solid #3a4552;
    outline: none;
}
QPushButton#filterButton {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    color: #d6dbe0;
    border-radius: 4px;
    padding: 8px 12px;
}
QPushButton#filterButton:hover {
    background-color: #2b3440;
}
QPushButton#filterButton:pressed {
    background-color: #34404d;
}
QFrame#card {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 6px;
}
QLabel#cardTitle {
    color: #ffffff;
    font-weight: bold;
    background: transparent;
}
QPushButton#cardButton {
    background-color: transparent;
    color: #d6dbe0;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton#cardButton:hover {
    background-color: #2b3440;
}
QPushButton#cardButton:pressed {
    background-color: #34404d;
}
QLabel#sectionTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
}
QFrame#separator {
    background-color: #3a4552;
    border: none;
}
QScrollArea#catalogScroll, QWidget#cardsContainer {
    background-color: transparent;
    border: none;
}
QFrame#datasetCard {
    background-color: #1a2027;
    border: 1px solid #3a4552;
    border-radius: 6px;
}
QFrame#datasetCard:hover {
    background-color: #1f2730;
    border: 1px solid #4a5868;
}
QLabel#datasetIcon {
    background-color: #2b3440;
    border-radius: 6px;
}
QLabel#datasetTitle {
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
}
QLabel#datasetSubtitle {
    color: #9aa5b1;
    font-size: 12px;
}
QLabel#badge {
    background-color: #2b3440;
    color: #d6dbe0;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 11px;
}
QLabel#statusBadge {
    border-radius: 6px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: bold;
}
QLabel#statusBadge[state="updated"] {
    background-color: #1f4d36;
    color: #6fd39b;
}
QLabel#statusBadge[state="update_available"] {
    background-color: #5a4318;
    color: #f0b95a;
}
QLabel#statusBadge[state="unchecked"] {
    background-color: #3a4552;
    color: #c4ccd4;
}
QLabel#statusBadge[state="error"] {
    background-color: #5a2323;
    color: #f08a8a;
}
QLabel#statusBadge[state="processing"] {
    background-color: #1f3d5a;
    color: #7fb8ea;
}
QPushButton#cardActionButton {
    background-color: transparent;
    color: #d6dbe0;
    border: 1px solid #3a4552;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton#cardActionButton:hover {
    background-color: #2b3440;
}
QPushButton#cardActionButton:pressed {
    background-color: #34404d;
}
QPushButton#cardDownloadButton {
    background-color: #3a6ea5;
    color: #fefefe;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton#cardDownloadButton:hover {
    background-color: #4a7fb8;
}
QPushButton#cardDownloadButton:pressed {
    background-color: #2f5c8a;
}
QLabel#pageSubtitle {
    color: #9aa5b1;
    font-size: 13px;
}
"""


WINDOW_OPACITY = 0.92
TOP_MARGIN = 16
MIN_WIDTH = 420
MAX_WIDTH = 900
COLLAPSED_HEIGHT = TITLE_BAR_HEIGHT + 2 * RESIZE_MARGIN  # só a barra de título, com as margens
EXPAND_DELAY_MS = 450
COLLAPSE_DELAY_MS = 400
ANIMATION_MS = 180


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dados do Amazonas")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # cantos arredondados
        self.setWindowOpacity(WINDOW_OPACITY)

        # Recolhida (estreita) por padrão; expande ao passar o mouse e recolhe ao sair.
        self._expanded = False
        self._animation = QPropertyAnimation(self, b"geometry", self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.setInterval(COLLAPSE_DELAY_MS)
        self._collapse_timer.timeout.connect(self._collapse_if_mouse_outside)
        # Só expande se o mouse ficar um instante em cima: passar rápido não "assusta".
        self._expand_timer = QTimer(self)
        self._expand_timer.setSingleShot(True)
        self._expand_timer.setInterval(EXPAND_DELAY_MS)
        self._expand_timer.timeout.connect(self._expand_if_mouse_inside)
        arrow_down = Path(__file__).resolve().parents[2] / "arrow_down.png"
        self._stylesheet = (
            STYLESHEET.replace("ARROW_DOWN_PATH", arrow_down.as_posix()) + TITLE_BAR_STYLESHEET
        )

        self._container = ResizableContainer()
        self.setCentralWidget(self._container)

        root = QVBoxLayout(self._container)
        root.setContentsMargins(RESIZE_MARGIN, RESIZE_MARGIN, RESIZE_MARGIN, RESIZE_MARGIN)
        root.setSpacing(0)

        self._title_bar = TitleBar(self, self.windowTitle())
        root.addWidget(self._title_bar)

        self._body = QWidget()
        layout = QHBoxLayout(self._body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Recorte do corpo: ao recolher a janela, o corpo é cortado em vez de espremido.
        clip = QScrollArea()
        clip.setWidgetResizable(True)
        clip.setFrameShape(QFrame.NoFrame)
        clip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)  # pode ficar com altura 0
        clip.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        clip.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        clip.viewport().setAutoFillBackground(False)
        clip.setWidget(self._body)
        self._body.setAutoFillBackground(False)  # o setWidget liga o preenchimento cinza padrão
        root.addWidget(clip, 1)

        self.sidebar = Sidebar()
        self.sidebar.theme_toggle_requested.connect(self._toggle_theme)
        layout.addWidget(self.sidebar)
        layout.addStretch(1)

        self._theme = settings.load()["aparencia"]["tema"]
        if self._theme not in (DARK, LIGHT):
            self._theme = DARK
        self._apply_theme()

        # Mínimo explícito (o layout não força o do conteúdo) + corpo com altura fixa: ao recolher,
        # a janela encolhe até a barra de título e o corpo é cortado em vez de espremido.
        self.setMinimumSize(MIN_WIDTH, COLLAPSED_HEIGHT)
        full_height = self._target_rect(expanded=True).height()
        self._body.setMinimumHeight(full_height - TITLE_BAR_HEIGHT - 2 * RESIZE_MARGIN)
        self.setGeometry(self._target_rect(expanded=False))

    def _target_rect(self, expanded: bool) -> QRect:
        """Retângulo centralizado e colado ao topo. Recolhida: só a barra de título; expandida: altura cheia."""
        area = (self.screen() or QGuiApplication.primaryScreen()).availableGeometry()
        width = max(MIN_WIDTH, min(MAX_WIDTH, int(area.width() * 0.6)))
        height = min(600, int(area.height() * 0.8)) if expanded else COLLAPSED_HEIGHT
        return QRect(area.x() + (area.width() - width) // 2, area.y() + TOP_MARGIN, width, height)

    def _set_expanded(self, expanded: bool) -> None:
        if self.isMaximized() or expanded == self._expanded:
            return
        self._expanded = expanded
        self._animation.stop()
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(self._target_rect(expanded))
        self._animation.start()

    def enterEvent(self, event) -> None:
        self._collapse_timer.stop()
        if self._expanded:
            self._expand_timer.stop()
        else:
            self._expand_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._expand_timer.stop()
        self._collapse_timer.start()
        super().leaveEvent(event)

    def _expand_if_mouse_inside(self) -> None:
        if self.geometry().contains(QCursor.pos()):
            self._set_expanded(True)

    def _collapse_if_mouse_outside(self) -> None:
        if QApplication.mouseButtons() != Qt.NoButton:  # arrastando ou redimensionando
            self._collapse_timer.start()
        elif not self.geometry().contains(QCursor.pos()):
            self._set_expanded(False)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            maximized = self.isMaximized()
            self._container.set_maximized(maximized)
            self._title_bar.set_maximized(maximized)

    def _apply_theme(self) -> None:
        self.setStyleSheet(apply_theme(self._stylesheet, self._theme))
        self.sidebar.set_theme(self._theme)
        self._title_bar.set_icon_color(ICON_COLORS[self._theme])

    def _toggle_theme(self) -> None:
        self._theme = DARK if self._theme == LIGHT else LIGHT
        self._apply_theme()
        current = settings.load()
        current["aparencia"]["tema"] = self._theme
        try:
            settings.save(current)
        except OSError:
            pass  # sem permissão para gravar: o tema vale só nesta sessão
