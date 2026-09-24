from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.ui.dataset_details import DatasetDetails

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Card(QFrame):
    def __init__(self, title: str, button_text: str = "", icon: str = "", expand_body: bool = False, parent=None):
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
        self.header_button.setVisible(bool(button_text or icon))  # sem texto nem ícone: não mostra
        if icon:
            self.header_button.setIcon(QIcon(str(PROJECT_ROOT / icon)))
            self.header_button.setIconSize(QSize(14, 14))
        header.addWidget(self.header_button)
        layout.addLayout(header)

        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        if expand_body:
            layout.addLayout(self.body_layout, 1)  # o corpo (ex.: uma área rolável) ocupa o espaço
        else:
            layout.addLayout(self.body_layout)
            layout.addStretch(1)  # corpo vazio não absorve espaço; o stretch mantém o título no topo


class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Detalhes do dataset selecionado: o conteúdo mais útil, então ganha mais espaço.
        self.details_card = Card("Detalhes do dataset", expand_body=True)
        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.details = DatasetDetails()
        scroll.setWidget(self.details)
        self.details_card.body_layout.addWidget(scroll)
        layout.addWidget(self.details_card, 3)

        self.process_card = Card("Processo de download e tratamento", icon="x.png")
        layout.addWidget(self.process_card, 1)

        self.recent_card = Card("Downloads recentes", "Ver todos  ", "seta.png")
        self.recent_card.header_button.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.recent_card, 1)
