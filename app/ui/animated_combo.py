from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtWidgets import QComboBox


POPUP_STYLE = """
QFrame {
    background-color: #212830;
    border: 1px solid #3a4552;
}
"""


class AnimatedComboBox(QComboBox):
    """QComboBox cujo popup desliza (cresce em altura) ao abrir."""

    SLIDE_DURATION_MS = 160

    def showPopup(self) -> None:
        super().showPopup()
        # O container do popup é a janela que contém a lista de itens.
        popup = self.view().window()
        popup.setStyleSheet(POPUP_STYLE)
        if popup.layout() is not None:
            popup.layout().setContentsMargins(0, 0, 0, 0)

        # Alinha o popup ao combo: mesma largura, mesma posição x e topo na mesma altura.
        combo_top_left = self.mapToGlobal(self.rect().topLeft())
        end = popup.geometry()
        end.moveTo(combo_top_left.x(), combo_top_left.y())
        end.setWidth(self.width())

        # Se o popup não cabe abaixo do topo do combo, ancora a base; senão, o topo.
        opens_above = end.bottom() > self.screen().availableGeometry().bottom()
        if opens_above:
            end.moveBottom(self.mapToGlobal(self.rect().bottomLeft()).y())
        start_height = 1
        if opens_above:
            start = QRect(end.x(), end.bottom() - start_height + 1, end.width(), start_height)
        else:
            start = QRect(end.x(), end.y(), end.width(), start_height)

        popup.setGeometry(start)
        self._slide = QPropertyAnimation(popup, b"geometry", self)
        self._slide.setDuration(self.SLIDE_DURATION_MS)
        self._slide.setStartValue(start)
        self._slide.setEndValue(end)
        self._slide.setEasingCurve(QEasingCurve.OutCubic)
        self._slide.start()
