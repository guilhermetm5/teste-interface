from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout

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

        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        for index, item in enumerate(SIDEBAR_ITEMS):
            button = QPushButton(item["label"])
            button.setObjectName("sidebarButton")
            button.setCheckable(True)
            button.clicked.connect(
                lambda _checked, item_id=item["id"]: self.item_selected.emit(item_id)
            )
            self._button_group.addButton(button)
            layout.addWidget(button)
            if index == 0:
                button.setChecked(True)

        layout.addStretch()
