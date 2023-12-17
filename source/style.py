# This file is part of pixelart-palette-converter.
# Copyright (C) 2023  Jan Mittendorf
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import typing

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPalette
from PyQt6.QtWidgets import (
    QCommonStyle,
    QStyle,
    QStyleOption,
    QStyleOptionComplex,
    QStyleOptionFrame,
    QStyleOptionGroupBox,
    QWidget,
)


class AppFont(QFont):
    def __init__(self):
        super().__init__("Century Gothic", pointSize=11)


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

    def drawComplexControl(
        self,
        control: QStyle.ComplexControl,
        option: QStyleOptionComplex,
        painter: QPainter,
        widget: QWidget,
    ) -> None:
        match control:
            case QStyle.ComplexControl.CC_GroupBox:
                # Implementation adapted from:
                # https://github.com/qt/qtbase/blob/dev/src/widgets/styles/qcommonstyle.cpp

                group_box_option = typing.cast(QStyleOptionGroupBox, option)

                # Draw frame
                frame_option = QStyleOptionFrame()
                frame_option.rect = self.subControlRect(
                    control, option, QStyle.SubControl.SC_GroupBoxFrame, widget
                )

                self.drawPrimitive(
                    QStyle.PrimitiveElement.PE_FrameGroupBox,
                    frame_option,
                    painter,
                    widget,
                )

                # Draw title
                text_rect = self.subControlRect(
                    control, option, QStyle.SubControl.SC_GroupBoxLabel, widget
                )
                text_rect.moveCenter(frame_option.rect.center())
                text_rect.moveTop(12)

                if not group_box_option.text == "":
                    self.drawItemText(
                        painter,
                        text_rect,
                        Qt.AlignmentFlag.AlignCenter,
                        group_box_option.palette,
                        QStyle.StateFlag.State_Enabled in group_box_option.state,
                        group_box_option.text,
                        QPalette.ColorRole.WindowText,
                    )
            case _:
                super().drawComplexControl(control, option, painter, widget)
