from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from app.ui.sidebar_items import SIDEBAR_ITEMS


class Sidebar(QFrame):
    item_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        for item in SIDEBAR_ITEMS:
            button = QPushButton(item["label"])
            button.setObjectName("sidebarButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda _checked, item_id=item["id"]: self.item_selected.emit(item_id)
            )
            layout.addWidget(button)

        layout.addStretch()
