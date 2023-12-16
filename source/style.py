from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPalette
from PyQt6.QtWidgets import QCommonStyle, QStyle, QStyleOption, QWidget


class AppFont(QFont):
    def __init__(self):
        super().__init__("Century Gothic", pointSize=10)


class AppPalette(QPalette):
    def __init__(self):
        super().__init__()

        # Background of QMainWindow, QWidget, QGroupBox etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.Window, QColor(16, 20, 24)
        )
        # Text inside QGroupBox, Frame of QComboBox menu etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.WindowText, Qt.GlobalColor.white
        )
        # Background of QSpinBox, QListWidget etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.Base, QColor(32, 40, 48)
        )

        # Title Text of QGroupBox, Text in QSpinBox, QComboBox etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.Text, Qt.GlobalColor.white
        )
        # Background of QPushButton, QCheckBox etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.Button, Qt.GlobalColor.darkCyan
        )
        # Text on QPushButton etc.
        self.setColor(
            QPalette.ColorGroup.All, QPalette.ColorRole.ButtonText, Qt.GlobalColor.white
        )


class AppStyle(QCommonStyle):
    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget,
    ) -> None:
        match element:
            case QStyle.PrimitiveElement.PE_PanelButtonCommand:
                radius = option.rect.height() / 2

                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(option.palette.button())
                painter.drawRoundedRect(option.rect, radius, radius)
            case QStyle.PrimitiveElement.PE_FrameGroupBox:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(option.palette.base())
                painter.drawRoundedRect(option.rect, 16, 16)
                return
            case _:
                super().drawPrimitive(element, option, painter, widget)
