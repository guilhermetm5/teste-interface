from pathlib import Path

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core import settings
from app.core.version import get_local_commit
from app.ui.animated_combo import AnimatedComboBox
from app.ui.home_page import Panel, hline
from app.ui.updates_page import make_icon_button, make_label

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENCODINGS = [("UTF-8", "utf-8"), ("UTF-8 com BOM", "utf-8-sig"), ("Latin-1 (ISO-8859-1)", "latin-1")]
SEPARATORS = [("Ponto e vírgula ( ; )", ";"), ("Vírgula ( , )", ","), ("Barra vertical ( | )", "|"), ("Tabulação", "\t")]

# Última verificação de dados: valor de exemplo (ainda não há onde ler isso).
LAST_CHECK_SAMPLE = "23/09/2026 10:24"


class ToggleSwitch(QAbstractButton):
    """Interruptor liga/desliga."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(40, 22)

    def sizeHint(self) -> QSize:
        return QSize(40, 22)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#3a8ee6" if self.isChecked() else "#3a4552"))
        painter.drawRoundedRect(self.rect(), self.height() / 2, self.height() / 2)
        knob = self.height() - 6
        x = self.width() - knob - 3 if self.isChecked() else 3
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(x, 3, knob, knob)


def setting_row(title: str, description: str, control: QWidget) -> QWidget:
    """Linha: título e descrição à esquerda, controle à direita."""
    row = QWidget()
    h = QHBoxLayout(row)
    h.setContentsMargins(0, 2, 0, 2)
    h.setSpacing(12)
    texts = QVBoxLayout()
    texts.setSpacing(1)
    texts.addWidget(make_label(title, "rowValue"))
    if description:
        desc = make_label(description, "datasetSubtitle")
        desc.setWordWrap(True)
        texts.addWidget(desc)
    h.addLayout(texts, 1)
    h.addWidget(control, 0, Qt.AlignVCenter)
    return row


def make_combo(options: list) -> AnimatedComboBox:
    combo = AnimatedComboBox()
    combo.setObjectName("filterCombo")
    for text, value in options:
        combo.addItem(text, value)
    combo.setFixedWidth(190)
    return combo


class SettingsPage(QWidget):
    # Pede à MainWindow para verificar atualizações do próprio aplicativo.
    check_app_update = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addLayout(self._build_header())

        scroll = QScrollArea()
        scroll.setObjectName("catalogScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setObjectName("cardsContainer")
        scroll.setWidget(content)
        grid = QGridLayout(content)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.addWidget(self._build_collect(), 0, 0)
        grid.addWidget(self._build_verification(), 0, 1)
        grid.addWidget(self._build_files(), 1, 0)
        grid.addWidget(self._build_app(), 1, 1)
        root.addWidget(scroll, 1)

        root.addLayout(self._build_footer())
        self.load_values()

    # --- blocos ---------------------------------------------------------------

    def _build_header(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(12)
        icon = QLabel()
        icon.setObjectName("datasetIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QIcon(str(PROJECT_ROOT / "config.png")).pixmap(QSize(24, 24)))
        h.addWidget(icon, 0, Qt.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        titles.addWidget(make_label("Configurações", "pageTitle"))
        titles.addWidget(make_label("Defina como o aplicativo coleta e salva os dados.", "pageSubtitle"))
        h.addLayout(titles, 1)
        return h

    def _build_collect(self) -> Panel:
        panel = Panel("↓", "Coleta de dados", "Controle como as coletas são executadas")

        self.output_dir = QLineEdit()
        self.output_dir.setObjectName("searchInput")
        self.choose_dir_button = make_icon_button("Alterar", "cardActionButton")
        self.choose_dir_button.clicked.connect(self._choose_dir)
        panel.body.addWidget(make_label("Pasta de saída", "rowValue"))
        folder = QHBoxLayout()
        folder.setSpacing(8)
        folder.addWidget(self.output_dir, 1)
        folder.addWidget(self.choose_dir_button)
        panel.body.addLayout(folder)
        panel.body.addWidget(hline())

        self.per_dataset = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Organizar por dataset", "Cria uma pasta separada para cada dataset", self.per_dataset))
        panel.body.addWidget(hline())
        self.save_logs = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Registrar logs das coletas", "Guarda o registro de cada coleta executada", self.save_logs))
        return panel

    def _build_verification(self) -> Panel:
        panel = Panel("↻", "Verificação de dados", "Defina quando checar se há dados novos")

        self.check_on_start = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Verificar ao iniciar o aplicativo", "Busca dados novos sempre que o app abre", self.check_on_start))
        panel.body.addWidget(hline())

        panel.body.addWidget(make_label("Ao encontrar atualização", "rowValue"))
        self.behavior_group = QButtonGroup(self)
        self.behavior_radios = {}
        for value, text in (("avisar", "Apenas avisar"), ("perguntar", "Perguntar antes de coletar")):
            radio = QRadioButton(text)
            radio.setObjectName("settingRadio")
            radio.setCursor(Qt.PointingHandCursor)
            self.behavior_group.addButton(radio)
            self.behavior_radios[value] = radio
            panel.body.addWidget(radio)
        panel.body.addWidget(hline())

        last = QHBoxLayout()
        last.addWidget(make_label("Última verificação", "metricLabel"))
        last.addStretch()
        last.addWidget(make_label(LAST_CHECK_SAMPLE, "rowValue"))
        panel.body.addLayout(last)
        self.check_now_button = make_icon_button("↻  Verificar agora", "outlineButton")
        panel.body.addWidget(self.check_now_button)
        return panel

    def _build_files(self) -> Panel:
        panel = Panel("▤", "Arquivos", "Comportamento dos CSVs gerados")

        self.encoding = make_combo(ENCODINGS)
        panel.body.addWidget(setting_row("Codificação", "", self.encoding))
        self.separator = make_combo(SEPARATORS)
        panel.body.addWidget(setting_row("Separador", "", self.separator))
        panel.body.addWidget(hline())

        self.include_origin = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Incluir origem_dado", "Coluna com a fonte de cada registro", self.include_origin))
        self.include_date = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Incluir data_coleta", "Coluna com a data em que o dado foi coletado", self.include_date))
        panel.body.addWidget(hline())
        self.keep_versions = ToggleSwitch()
        panel.body.addWidget(setting_row(
            "Manter versões anteriores", "Ao gerar uma nova versão, não apaga a anterior", self.keep_versions))
        return panel

    def _build_app(self) -> Panel:
        panel = Panel("⚙", "Aplicativo", "Informações e manutenção do aplicativo")

        commit = get_local_commit()
        version = commit[:7] if commit else "desconhecida"
        info = QHBoxLayout()
        info.addWidget(make_label("Versão da aplicação", "metricLabel"))
        info.addStretch()
        info.addWidget(make_label(version, "rowValue"))
        panel.body.addLayout(info)
        panel.body.addWidget(hline())

        self.app_update_button = make_icon_button("↻  Verificar atualizações do aplicativo", "outlineButton")
        self.app_update_button.clicked.connect(self._on_check_app_update)
        panel.body.addWidget(self.app_update_button)
        self.app_update_status = make_label("", "datasetSubtitle")
        panel.body.addWidget(self.app_update_status)
        return panel

    def _build_footer(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(8)
        self.status_label = make_label("", "datasetSubtitle")
        h.addWidget(self.status_label)
        h.addStretch()
        self.cancel_button = make_icon_button("✕  Cancelar", "cardActionButton")
        self.cancel_button.clicked.connect(self._on_cancel)
        self.save_button = make_icon_button("Salvar alterações", "saveButton")
        self.save_button.clicked.connect(self._on_save)
        h.addWidget(self.cancel_button)
        h.addWidget(self.save_button)
        return h

    # --- valores --------------------------------------------------------------

    def load_values(self) -> None:
        """Preenche os controles com o que está salvo em disco."""
        s = settings.load()
        self.output_dir.setText(s["coleta"]["pasta_saida"])
        self.per_dataset.setChecked(s["coleta"]["pasta_por_dataset"])
        self.save_logs.setChecked(s["coleta"]["registrar_logs"])

        self.check_on_start.setChecked(s["verificacao"]["verificar_ao_iniciar"])
        behavior = s["verificacao"]["comportamento"]
        self.behavior_radios.get(behavior, self.behavior_radios["avisar"]).setChecked(True)

        self._select_data(self.encoding, s["arquivos"]["codificacao"])
        self._select_data(self.separator, s["arquivos"]["separador"])
        self.include_origin.setChecked(s["arquivos"]["incluir_origem_dado"])
        self.include_date.setChecked(s["arquivos"]["incluir_data_coleta"])
        self.keep_versions.setChecked(s["arquivos"]["manter_versoes"])

    def collect_values(self) -> dict:
        """Lê os controles e devolve o dict de configurações."""
        s = settings.load()
        s["coleta"]["pasta_saida"] = self.output_dir.text().strip() or settings.DEFAULTS["coleta"]["pasta_saida"]
        s["coleta"]["pasta_por_dataset"] = self.per_dataset.isChecked()
        s["coleta"]["registrar_logs"] = self.save_logs.isChecked()

        s["verificacao"]["verificar_ao_iniciar"] = self.check_on_start.isChecked()
        s["verificacao"]["comportamento"] = next(
            value for value, radio in self.behavior_radios.items() if radio.isChecked()
        )

        s["arquivos"]["codificacao"] = self.encoding.currentData()
        s["arquivos"]["separador"] = self.separator.currentData()
        s["arquivos"]["incluir_origem_dado"] = self.include_origin.isChecked()
        s["arquivos"]["incluir_data_coleta"] = self.include_date.isChecked()
        s["arquivos"]["manter_versoes"] = self.keep_versions.isChecked()
        return s

    @staticmethod
    def _select_data(combo: AnimatedComboBox, value: str) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)

    # --- ações ----------------------------------------------------------------

    def _choose_dir(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Escolher pasta de saída", self.output_dir.text())
        if chosen:
            self.output_dir.setText(str(Path(chosen)))

    def _flash(self, label: QLabel, text: str, ms: int = 2500) -> None:
        label.setText(text)
        QTimer.singleShot(ms, lambda: label.setText(""))

    def _on_save(self) -> None:
        try:
            settings.save(self.collect_values())
        except OSError as exc:
            self._flash(self.status_label, f"Não foi possível salvar: {exc}", 5000)
            return
        self._flash(self.status_label, "Alterações salvas.")

    def _on_cancel(self) -> None:
        self.load_values()
        self._flash(self.status_label, "Alterações descartadas.")

    def _on_check_app_update(self) -> None:
        self.check_app_update.emit()
        self._flash(self.app_update_status, "Verificando... o aviso aparece no topo se houver atualização.", 4000)


SETTINGS_STYLESHEET = """
QRadioButton#settingRadio {
    color: #d6dbe0;
    spacing: 8px;
    padding: 2px 0;
}
QRadioButton#settingRadio::indicator {
    width: 12px;
    height: 12px;
    border-radius: 7px;
    border: 1px solid #5a6878;
    background-color: transparent;
}
QRadioButton#settingRadio::indicator:hover { border: 1px solid #3a8ee6; }
QRadioButton#settingRadio::indicator:checked {
    width: 6px;
    height: 6px;
    border: 4px solid #3a8ee6;
    background-color: #ffffff;
}

QPushButton#outlineButton {
    background-color: transparent;
    color: #8fc1f0;
    border: 1px solid #2f5a8a;
    border-radius: 4px;
    padding: 8px 14px;
}
QPushButton#outlineButton:hover   { background-color: #1c2a3a; }
QPushButton#outlineButton:pressed { background-color: #243447; }

QPushButton#saveButton {
    background-color: #3a6ea5;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton#saveButton:hover   { background-color: #4a7fb8; }
QPushButton#saveButton:pressed { background-color: #2f5c8a; }
"""
