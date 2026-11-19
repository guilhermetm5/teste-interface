from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

RESIZE_MARGIN = 6

TITLE_BAR_STYLESHEET = """
QWidget#content {
    border: 1px solid #3a4552;
}
QFrame#titleBar {
    background-color: #1a2027;
}
QLabel#titleBarLabel {
    color: #9aa5b1;
    font-size: 12px;
}
QPushButton#titleButton, QPushButton#titleCloseButton {
    background-color: transparent;
    color: #d6dbe0;
    border: none;
    border-radius: 0;
    font-size: 13px;
}
QPushButton#titleButton:hover {
    background-color: #2b3440;
}
QPushButton#titleCloseButton:hover {
    background-color: #c42b1c;
    color: #fefefe;
}
"""

_CURSORS = {
    Qt.LeftEdge: Qt.SizeHorCursor,
    Qt.RightEdge: Qt.SizeHorCursor,
    Qt.TopEdge: Qt.SizeVerCursor,
    Qt.BottomEdge: Qt.SizeVerCursor,
    Qt.LeftEdge | Qt.TopEdge: Qt.SizeFDiagCursor,
    Qt.RightEdge | Qt.BottomEdge: Qt.SizeFDiagCursor,
    Qt.RightEdge | Qt.TopEdge: Qt.SizeBDiagCursor,
    Qt.LeftEdge | Qt.BottomEdge: Qt.SizeBDiagCursor,
}


def window_icon(kind: str, color: str) -> QIcon:
    """Ícone de controle de janela desenhado por código (não depende de fonte)."""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor(color), 2))
    painter.setBrush(Qt.NoBrush)
    if kind == "minimize":
        painter.drawLine(QPointF(5, 12), QPointF(19, 12))
    elif kind == "maximize":
        painter.drawRect(QRectF(5.5, 5.5, 13, 13))
    elif kind == "restore":
        painter.drawRect(QRectF(5.5, 9.5, 9, 9))
        back = QPainterPath(QPointF(9.5, 9.5))
        back.lineTo(9.5, 5.5)
        back.lineTo(18.5, 5.5)
        back.lineTo(18.5, 14.5)
        back.lineTo(14.5, 14.5)
        painter.drawPath(back)
    else:  # close
        painter.drawLine(QPointF(6, 6), QPointF(18, 18))
        painter.drawLine(QPointF(18, 6), QPointF(6, 18))
    painter.end()
    return QIcon(pixmap)


class TitleBar(QFrame):
    """Barra de título própria: arrastar a janela, minimizar, maximizar e fechar."""

    def __init__(self, window: QWidget, title: str):
        super().__init__()
        self.setObjectName("titleBar")
        self.setFixedHeight(32)
        self._window = window

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(title)
        label.setObjectName("titleBarLabel")
        layout.addWidget(label)
        layout.addStretch()

        self._min_button = self._button("titleButton", window.showMinimized)
        self._max_button = self._button("titleButton", self._toggle_maximize)
        self._close_button = self._button("titleCloseButton", window.close)
        for button in (self._min_button, self._max_button, self._close_button):
            layout.addWidget(button)

        self._icon_color = "#ffffff"
        self._maximized = False
        self._refresh_icons()

    def _button(self, name: str, slot) -> QPushButton:
        button = QPushButton()
        button.setObjectName(name)
        button.setIconSize(QSize(12, 12))
        button.setFixedSize(46, 32)
        button.setFocusPolicy(Qt.NoFocus)
        button.clicked.connect(slot)
        return button

    def _toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def set_maximized(self, maximized: bool) -> None:
        self._maximized = maximized
        self._refresh_icons()

    def set_icon_color(self, color: str) -> None:
        self._icon_color = color
        self._refresh_icons()

    def _refresh_icons(self) -> None:
        color = self._icon_color
        self._min_button.setIcon(window_icon("minimize", color))
        self._max_button.setIcon(window_icon("restore" if self._maximized else "maximize", color))
        close = window_icon("close", color)
        close.addPixmap(window_icon("close", "#fefefe").pixmap(24, 24), QIcon.Active)  # branco sobre o vermelho
        self._close_button.setIcon(close)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._window.windowHandle() is not None:
            self._window.windowHandle().startSystemMove()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._toggle_maximize()
        super().mouseDoubleClickEvent(event)


class ResizableContainer(QWidget):
    """Fundo da janela sem borda: a faixa de margem em volta serve de alça de redimensionamento."""

    def __init__(self):
        super().__init__()
        self.setObjectName("content")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)

    def _edges(self, pos):
        if self.window().isMaximized():
            return Qt.Edges()
        edges = Qt.Edges()
        if pos.x() < RESIZE_MARGIN:
            edges |= Qt.LeftEdge
        elif pos.x() >= self.width() - RESIZE_MARGIN:
            edges |= Qt.RightEdge
        if pos.y() < RESIZE_MARGIN:
            edges |= Qt.TopEdge
        elif pos.y() >= self.height() - RESIZE_MARGIN:
            edges |= Qt.BottomEdge
        return edges

    def mouseMoveEvent(self, event) -> None:
        cursor = _CURSORS.get(self._edges(event.position().toPoint()))
        if cursor is None:
            self.unsetCursor()
        else:
            self.setCursor(cursor)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        edges = self._edges(event.position().toPoint())
        handle = self.window().windowHandle()
        if event.button() == Qt.LeftButton and edges and handle is not None:
            handle.startSystemResize(edges)
            return
        super().mousePressEvent(event)

    def set_maximized(self, maximized: bool) -> None:
        margin = 0 if maximized else RESIZE_MARGIN
        self.layout().setContentsMargins(margin, margin, margin, margin)
