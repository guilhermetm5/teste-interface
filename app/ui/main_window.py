from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.updater import UpdateCheckWorker
from app.core.version import get_local_commit
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
QPushButton#sidebarButton:checked {
    background-color: #34404d;
    color: #ffffff;
}
QLabel#contentLabel {
    color: #d6dbe0;
    font-size: 16px;
}
QLabel#updateBanner {
    background-color: #3a6ea5;
    color: #ffffff;
    padding: 6px 10px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste Interface")
        self.resize(900, 600)
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        central.setObjectName("content")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.update_banner = QLabel()
        self.update_banner.setObjectName("updateBanner")
        self.update_banner.setVisible(False)
        root_layout.addWidget(self.update_banner)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        root_layout.addWidget(body)

        self.sidebar = Sidebar()
        self.sidebar.item_selected.connect(self._on_item_selected)
        body_layout.addWidget(self.sidebar)

        self.content_label = QLabel("Selecione um item na sidebar")
        self.content_label.setObjectName("contentLabel")
        body_layout.addWidget(self.content_label)
        body_layout.addStretch()

        self._local_commit = get_local_commit()
        self._update_worker: UpdateCheckWorker | None = None
        self.check_for_update()

    def _on_item_selected(self, item_id: str) -> None:
        self.content_label.setText(f"Você selecionou: {item_id}")

    def check_for_update(self) -> None:
        self._update_worker = UpdateCheckWorker()
        self._update_worker.finished_ok.connect(self._on_update_check_ok)
        self._update_worker.finished_error.connect(self._on_update_check_error)
        self._update_worker.start()

    def _on_update_check_ok(self, info: dict) -> None:
        remote_sha = info["sha"]
        if self._local_commit and remote_sha == self._local_commit:
            return
        self.update_banner.setText(
            f"Nova atualização disponível: {info['message']} ({remote_sha[:7]})"
        )
        self.update_banner.setVisible(True)

    def _on_update_check_error(self, message: str) -> None:
        # Falha silenciosa (ex: sem internet) não deve atrapalhar o uso do app.
        pass
