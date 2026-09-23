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
from app.ui.sidebar import Sidebar

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
QComboBox#filterCombo QAbstractItemView {
    background-color: #1a2027;
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
QFrame#separator {
    background-color: #3a4552;
    border: none;
}
QListWidget#catalogList {
    background-color: transparent;
    border: none;
    color: #d6dbe0;
    outline: none;
}
QListWidget#catalogList::item {
    padding: 8px 12px;
    border-radius: 4px;
}
QListWidget#catalogList::item:hover {
    background-color: #2b3440;
}
QListWidget#catalogList::item:selected {
    background-color: #34404d;
    color: #ffffff;
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
        self.setStyleSheet(STYLESHEET)

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
        self.pages.addWidget(self._catalogo_page)
        self.pages.addWidget(self.content_label)
        self.pages.setCurrentWidget(self._catalogo_page)
        body_layout.addWidget(self.pages, 1)

        self._local_commit = get_local_commit()
        self._update_worker: UpdateCheckWorker | None = None
        self.check_for_update()

    def _on_item_selected(self, item_id: str) -> None:
        if item_id == "catalogo":
            self.pages.setCurrentWidget(self._catalogo_page)
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
