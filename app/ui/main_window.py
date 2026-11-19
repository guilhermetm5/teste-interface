from pathlib import Path

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from app.core import settings
from app.ui.frameless import RESIZE_MARGIN, TITLE_BAR_STYLESHEET, ResizableContainer, TitleBar
from app.ui.sidebar import Sidebar
from app.ui.theme import DARK, ICON_COLORS, LIGHT, apply_theme

STYLESHEET = """
QMainWindow, QWidget#content {
    background-color: #212830;
}
QFrame#sidebar {
    background-color: #1a2027;
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dados do Amazonas")
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.resize(900, 600)
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

        body = QWidget()
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        root.addWidget(body, 1)

        self.sidebar = Sidebar()
        self.sidebar.theme_toggle_requested.connect(self._toggle_theme)
        layout.addWidget(self.sidebar)
        layout.addStretch(1)

        self._theme = settings.load()["aparencia"]["tema"]
        if self._theme not in (DARK, LIGHT):
            self._theme = DARK
        self._apply_theme()

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
