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

import ast
from abc import abstractmethod
from typing import override

from PIL import Image, ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPixmap, QResizeEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from source.conversion import convert_image
from source.typing import RGBColor


class GUI(QWidget):
    def __init__(
        self, parent: QWidget | None = None, flags: Qt.WindowType | None = None
    ):
        if flags is None:
            super().__init__(parent)
        else:
            super().__init__(parent, flags)

        input_image_group_box = InputImageGroupBox()
        output_image_group_box = OutputImageGroupBox()
        parameter_group_box = ParameterGroupBox(
            input_image_group_box.image_label, output_image_group_box.image_label
        )

        layout = QHBoxLayout()
        layout.addWidget(parameter_group_box, stretch=1)
        layout.addWidget(input_image_group_box, stretch=1)
        layout.addWidget(output_image_group_box, stretch=1)

        self.setLayout(layout)


class ParameterGroupBox(QGroupBox):
    def __init__(
        self,
        input_image_label: "ImageLabel",
        output_image_label: "ImageLabel",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Parameters", parent)

        self._input_image_label = input_image_label
        self._output_image_label = output_image_label

        downsampling_label = QLabel("Downsampling factor:")

        self._downsampling_spin_box = QSpinBox()
        self._downsampling_spin_box.setMinimum(1)

        downsampling_layout = QHBoxLayout()
        downsampling_layout.addWidget(downsampling_label)
        downsampling_layout.addStretch(stretch=1)
        downsampling_layout.addWidget(self._downsampling_spin_box)

        resampling_label = QLabel("Resampling mode:")
        self._resampling_combo_box = QComboBox()

        for resampling_mode in Image.Resampling.__members__:
            self._resampling_combo_box.addItem(resampling_mode.capitalize())

        resampling_layout = QHBoxLayout()
        resampling_layout.addWidget(resampling_label)
        resampling_layout.addStretch(stretch=1)
        resampling_layout.addWidget(self._resampling_combo_box)

        self._grayscale_check_box = QCheckBox("Grayscale Conversion")

        colors_label = QLabel("Colors:")
        self._colors_list_widget = QListWidget()

        self._colors_add_push_button = QPushButton("Add")
        self._colors_add_push_button.clicked.connect(self._add_color)

        self._colors_edit_push_button = QPushButton("Edit")
        self._colors_edit_push_button.clicked.connect(self._edit_color)

        self._colors_remove_push_button = QPushButton("Remove")
        self._colors_remove_push_button.clicked.connect(self._remove_color)

        colors_bottom_layout = QHBoxLayout()
        colors_bottom_layout.addWidget(self._colors_add_push_button)
        colors_bottom_layout.addWidget(self._colors_edit_push_button)
        colors_bottom_layout.addWidget(self._colors_remove_push_button)

        convert_push_button = QPushButton("Convert Image")
        convert_push_button.clicked.connect(self._convert_image)

        layout = QVBoxLayout()
        layout.addLayout(downsampling_layout)
        layout.addLayout(resampling_layout)
        layout.addStretch(stretch=1)
        layout.addWidget(self._grayscale_check_box)
        layout.addStretch(stretch=1)
        layout.addWidget(colors_label)
        layout.addWidget(self._colors_list_widget)
        layout.addLayout(colors_bottom_layout)
        layout.addStretch(stretch=1)
        layout.addWidget(convert_push_button)

        self.setLayout(layout)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        )

    def _add_color(self) -> None:
        qcolor = QColorDialog.getColor()

        if qcolor.isValid():
            color = qcolor.getRgb()[:3]
            self._colors_list_widget.addItem(str(color))

    def _edit_color(self) -> None:
        selected_items = self._colors_list_widget.selectedItems()

        if not selected_items:
            return

        selected_item = selected_items[0]

        current_color = ast.literal_eval(selected_item.text())
        current_qcolor = QColor(*current_color)

        new_qcolor = QColorDialog.getColor(initial=current_qcolor)

        if new_qcolor.isValid():
            new_color = new_qcolor.getRgb()[:3]
            selected_item.setText(str(new_color))

    def _remove_color(self) -> None:
        current_row = self._colors_list_widget.currentRow()
        self._colors_list_widget.takeItem(current_row)

    def _convert_image(self) -> None:
        input_image_pixmap = self._input_image_label.default_pixmap

        if input_image_pixmap is None:
            return

        input_image = ImageQt.fromqpixmap(input_image_pixmap)

        downsampling_factor = self._downsampling_spin_box.value()

        if downsampling_factor == 1:
            downsampling_factor = None

        resampling_mode_str = self._resampling_combo_box.currentText()
        resampling_mode = Image.Resampling[resampling_mode_str.upper()]

        enable_grayscale = self._grayscale_check_box.isChecked()

        colors: list[RGBColor] | None = []

        for item_index in range(self._colors_list_widget.count()):
            item = self._colors_list_widget.item(item_index)

            if item is not None:
                colors.append(ast.literal_eval(item.text()))

        if not colors:
            colors = None

        converted_image = convert_image(
            input_image,
            downsampling_factor=downsampling_factor,
            resampling_mode=resampling_mode,
            grayscale=enable_grayscale,
            colors=colors,
        )
        converted_qimage = QImage(
            converted_image.tobytes(),
            converted_image.width,
            converted_image.height,
            converted_image.width * 3,
            QImage.Format.Format_RGB888,
        )
        converted_image_pixmap = QPixmap(converted_qimage)

        self._output_image_label.setPixmap(converted_image_pixmap)


class ImageLabel(QLabel):
    def __init__(
        self,
        transform_mode: Qt.TransformationMode = (
            Qt.TransformationMode.SmoothTransformation
        ),
        parent: QWidget | None = None,
        flags: Qt.WindowType | None = None,
    ) -> None:
        if flags is None:
            super().__init__(None, parent)
        else:
            super().__init__(None, parent, flags)

        self.default_pixmap: QPixmap | None = None
        self._transform_mode = transform_mode

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_resized_pixmap()

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.default_pixmap is not None:
            self.setPixmap(self.default_pixmap)

        super().resizeEvent(event)

    @override
    def setPixmap(self, pixmap: QPixmap) -> None:
        self.default_pixmap = pixmap
        self._set_resized_pixmap()

    def _set_resized_pixmap(self) -> None:
        if self.default_pixmap is not None:
            scaled_pixmap = self.default_pixmap.scaled(
                self.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=self._transform_mode,
            )

            super().setPixmap(scaled_pixmap)


class _ImageGroupBox(QGroupBox):
    def __init__(
        self,
        title: str,
        button_text: str,
        transform_mode: Qt.TransformationMode = (
            Qt.TransformationMode.SmoothTransformation
        ),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(title, parent)

        self.image_label = ImageLabel(transform_mode=transform_mode)

        self._push_button = QPushButton(button_text)
        self._push_button.clicked.connect(self._button_action)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self._push_button)

        self.setLayout(layout)

    @abstractmethod
    def _button_action(self):
        raise NotImplementedError()


class InputImageGroupBox(_ImageGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Original Image", "Select Image...", parent=parent)

    @override
    def _button_action(self) -> None:
        file_path = QFileDialog.getOpenFileName()[0]

        if file_path == "":
            return

        self.image_label.setPixmap(QPixmap(file_path))


class OutputImageGroupBox(_ImageGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Converted Image",
            "Save Converted Image...",
            transform_mode=Qt.TransformationMode.FastTransformation,
            parent=parent,
        )

    @override
    def _button_action(self) -> None:
        converted_image_pixmap = self.image_label.default_pixmap

        if converted_image_pixmap is None:
            return

        file_path = QFileDialog.getSaveFileName(filter="Images (*.png *.jpg)")[0]

        if file_path == "":
            return

        converted_image = ImageQt.fromqpixmap(converted_image_pixmap)
        converted_image.save(file_path)
