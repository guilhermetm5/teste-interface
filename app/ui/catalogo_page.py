from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QVBoxLayout, QWidget

CATALOGO_ITEMS = ["IBGE"]


class CatalogoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        title = QLabel("Catálogo")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        layout.addWidget(separator)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("catalogList")
        self.list_widget.addItems(CATALOGO_ITEMS)
        layout.addWidget(self.list_widget)
