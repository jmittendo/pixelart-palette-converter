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

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPalette, QRegion
from PyQt6.QtWidgets import (
    QCommonStyle,
    QStyle,
    QStyleOption,
    QStyleOptionButton,
    QStyleOptionComplex,
    QStyleOptionFocusRect,
    QStyleOptionFrame,
    QStyleOptionGroupBox,
    QWidget,
)


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
                text_rect = self.subControlRect(
                    control, option, QStyle.SubControl.SC_GroupBoxLabel, widget
                )
                check_box_rect = self.subControlRect(
                    control, option, QStyle.SubControl.SC_GroupBoxLabel, widget
                )

                if QStyle.SubControl.SC_GroupBoxFrame in group_box_option.subControls:
                    frame_option = QStyleOptionFrame()
                    # Missing: "frame.QStyleOption::operator=(*groupBox);"
                    frame_option.features = group_box_option.features
                    frame_option.lineWidth = group_box_option.lineWidth
                    frame_option.midLineWidth = group_box_option.midLineWidth
                    frame_option.rect = self.subControlRect(
                        control, option, QStyle.SubControl.SC_GroupBoxFrame, widget
                    )

                    # Missing: "QPainterStateSaver pss(p);"
                    region = QRegion(group_box_option.rect)

                    if not group_box_option.text == "":
                        ltr = (
                            group_box_option.direction is Qt.LayoutDirection.LeftToRight
                        )

                        if (
                            QStyle.SubControl.SC_GroupBoxCheckBox
                            in group_box_option.subControls
                        ):
                            final_rect = check_box_rect.united(text_rect)
                            final_rect.adjust(-4 if ltr else 0, 0, 0 if ltr else 4, 0)
                        else:
                            final_rect = text_rect

                        # Should be: "region -= final_rect;" but not possible in PyQt6
                        final_rect_negative_coords = [
                            -c for c in final_rect.getCoords() if c is not None
                        ]
                        negative_rect = QRect(*final_rect_negative_coords)

                        region = region + negative_rect

                    self.drawPrimitive(
                        QStyle.PrimitiveElement.PE_FrameGroupBox,
                        frame_option,
                        painter,
                        widget,
                    )

                # Draw title
                if (
                    QStyle.SubControl.SC_GroupBoxLabel in group_box_option.subControls
                    and not group_box_option.text == ""
                ):
                    text_color = group_box_option.textColor

                    if isinstance(text_color, QColor) and text_color.isValid():
                        painter.setPen(text_color)

                    alignment = int(group_box_option.textAlignment)

                    if not self.styleHint(
                        QStyle.StyleHint.SH_UnderlineShortcut, option, widget
                    ):
                        alignment |= Qt.TextFlag.TextHideMnemonic  # correct?

                    self.drawItemText(
                        painter,
                        text_rect,
                        Qt.TextFlag.TextShowMnemonic
                        | Qt.AlignmentFlag.AlignHCenter
                        | alignment,
                        group_box_option.palette,
                        QStyle.StateFlag.State_Enabled in group_box_option.state,
                        group_box_option.text,
                        QPalette.ColorRole.NoRole
                        if isinstance(text_color, QColor) and text_color.isValid()
                        else QPalette.ColorRole.WindowText,
                    )

                    if QStyle.StateFlag.State_HasFocus in group_box_option.state:
                        focus_rect_option = QStyleOptionFocusRect()
                        # Missing: "fropt.QStyleOption::operator=(*groupBox);"
                        focus_rect_option.rect = text_rect
                        self.drawPrimitive(
                            QStyle.PrimitiveElement.PE_FrameFocusRect,
                            focus_rect_option,
                            painter,
                            widget,
                        )

                # Draw checkbox
                if (
                    QStyle.SubControl.SC_GroupBoxCheckBox
                    in group_box_option.subControls
                ):
                    button_option = QStyleOptionButton()
                    # box.QStyleOption::operator=(*groupBox);
                    button_option.rect = check_box_rect
                    self.drawPrimitive(
                        QStyle.PrimitiveElement.PE_IndicatorCheckBox,
                        button_option,
                        painter,
                        widget,
                    )
            case _:
                super().drawComplexControl(control, option, painter, widget)
