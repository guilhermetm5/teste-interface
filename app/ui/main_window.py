from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.updater import UpdateCheckWorker
from app.core.version import get_local_commit, pull_latest, restart_app
from app.ui.catalogo_page import CatalogoPage
from app.ui.downloads_page import DOWNLOADS_STYLESHEET, DownloadsPage
from app.ui.home_page import HOME_STYLESHEET, HomePage
from app.ui.settings_page import SETTINGS_STYLESHEET, SettingsPage
from app.ui.sidebar import Sidebar
from app.ui.updates_page import UPDATES_STYLESHEET, UpdatesPage

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
    color: #ffffff;
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
QWidget#updateBanner {
    background-color: #3a6ea5;
}
QLabel#updateBannerLabel {
    color: #ffffff;
}
QPushButton#updateBannerButton {
    background-color: #ffffff;
    color: #3a6ea5;
    border: none;
    border-radius: 3px;
    padding: 4px 10px;
    font-weight: bold;
}
QPushButton#updateBannerButton:hover {
    background-color: #e0e8f0;
}
QPushButton#updateBannerButton:disabled {
    background-color: #c9d6e3;
    color: #6d7a87;
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
        self.resize(900, 600)
        arrow_down = Path(__file__).resolve().parents[2] / "arrow_down.png"
        self.setStyleSheet(
            STYLESHEET.replace("ARROW_DOWN_PATH", arrow_down.as_posix())
            + UPDATES_STYLESHEET
            + HOME_STYLESHEET
            + DOWNLOADS_STYLESHEET
            + SETTINGS_STYLESHEET
        )

        central = QWidget()
        central.setObjectName("content")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.update_banner = QWidget()
        self.update_banner.setObjectName("updateBanner")
        self.update_banner.setVisible(False)
        banner_layout = QHBoxLayout(self.update_banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)

        self.update_banner_label = QLabel()
        self.update_banner_label.setObjectName("updateBannerLabel")
        banner_layout.addWidget(self.update_banner_label)
        banner_layout.addStretch()

        self.update_banner_button = QPushButton("Atualizar agora")
        self.update_banner_button.setObjectName("updateBannerButton")
        self.update_banner_button.clicked.connect(self._on_update_clicked)
        banner_layout.addWidget(self.update_banner_button)

        root_layout.addWidget(self.update_banner)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        root_layout.addWidget(body)

        self.sidebar = Sidebar()
        self.sidebar.item_selected.connect(self._on_item_selected)
        body_layout.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.content_label = QLabel()
        self.content_label.setObjectName("contentLabel")
        self._catalogo_page = CatalogoPage()
        self._updates_page = UpdatesPage()
        self._home_page = HomePage()
        self._home_page.navigate.connect(self.sidebar.select)
        self._downloads_page = DownloadsPage()
        self._settings_page = SettingsPage()
        self._settings_page.check_app_update.connect(self.check_for_update)
        self.pages.addWidget(self._downloads_page)
        self.pages.addWidget(self._settings_page)
        self.pages.addWidget(self._home_page)
        self.pages.addWidget(self._catalogo_page)
        self.pages.addWidget(self._updates_page)
        self.pages.addWidget(self.content_label)
        self._on_item_selected("home")
        body_layout.addWidget(self.pages, 1)

        self._local_commit = get_local_commit()
        self._update_worker: UpdateCheckWorker | None = None
        self.check_for_update()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            self._catalogo_page.side_panel.setVisible(self.isMaximized())
            self._updates_page.detail_panel.setVisible(self.isMaximized())
            self._home_page.side_column.setVisible(self.isMaximized())
            self._downloads_page.detail_panel.setVisible(self.isMaximized())

    def _on_item_selected(self, item_id: str) -> None:
        if item_id == "home":
            self.pages.setCurrentWidget(self._home_page)
            return
        if item_id == "explore":
            self.pages.setCurrentWidget(self._catalogo_page)
            return
        if item_id == "config":
            self.pages.setCurrentWidget(self._settings_page)
            return
        if item_id == "download":
            self.pages.setCurrentWidget(self._downloads_page)
            return
        if item_id == "update":
            self.pages.setCurrentWidget(self._updates_page)
            return
        self.content_label.setText(f"Você selecionou: {item_id}")
        self.pages.setCurrentWidget(self.content_label)

    def check_for_update(self) -> None:
        self._update_worker = UpdateCheckWorker()
        self._update_worker.finished_ok.connect(self._on_update_check_ok)
        self._update_worker.finished_error.connect(self._on_update_check_error)
        self._update_worker.start()

    def _on_update_check_ok(self, info: dict) -> None:
        remote_sha = info["sha"]
        if self._local_commit and remote_sha == self._local_commit:
            return
        self.update_banner_label.setText(
            f"Nova atualização disponível: {info['message']} ({remote_sha[:7]})"
        )
        self.update_banner.setVisible(True)

    def _on_update_check_error(self, message: str) -> None:
        pass

    def _on_update_clicked(self) -> None:
        self.update_banner_button.setEnabled(False)
        self.update_banner_button.setText("Atualizando...")

        success, message = pull_latest()

        if not success:
            self.update_banner_label.setText(f"Falha ao atualizar: {message}")
            self.update_banner_button.setEnabled(True)
            self.update_banner_button.setText("Atualizar agora")
            return

        restart_app()
