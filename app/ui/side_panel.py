from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Card(QFrame):
    def __init__(self, title: str, button_text: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        header.addWidget(title_label)
        header.addStretch()

        self.header_button = QPushButton(button_text)
        self.header_button.setObjectName("cardButton")
        self.header_button.setCursor(Qt.PointingHandCursor)
        if icon:
            self.header_button.setIcon(QIcon(str(PROJECT_ROOT / icon)))
            self.header_button.setIconSize(QSize(14, 14))
        header.addWidget(self.header_button)
        layout.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.body_layout)
        layout.addStretch(1)


class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.process_card = Card("Processo de download e tratamento", icon="x.png")
        layout.addWidget(self.process_card, 1)

        self.recent_card = Card("Downloads recentes", "Ver todos  ", "seta.png")
        self.recent_card.header_button.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.recent_card, 1)
