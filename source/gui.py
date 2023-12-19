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
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from source.conversion import convert_image
from source.typing import RGBColor

PIXEL_PRESCALE_FACTOR_BASE = 4096


class GUI(QWidget):
    def __init__(
        self, parent: QWidget | None = None, flags: Qt.WindowType | None = None
    ) -> None:
        if flags is None:
            super().__init__(parent)
        else:
            super().__init__(parent, flags)

        image_group_box = ImageGroupBox()
        parameter_group_box = ParameterGroupBox(image_group_box)

        layout = QHBoxLayout()
        layout.addWidget(parameter_group_box, stretch=1)
        layout.addWidget(image_group_box, stretch=1)

        self.setLayout(layout)


class DownsamplingGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Downsampling", parent)

        factor_label = QLabel("Factor:")

        self._factor_spin_box = QSpinBox()
        self._factor_spin_box.setMinimum(1)

        factor_layout = QHBoxLayout()
        factor_layout.addWidget(factor_label)
        factor_layout.addStretch(stretch=1)
        factor_layout.addWidget(self._factor_spin_box)

        resampling_label = QLabel("Resampling mode:")

        self._resampling_combo_box = QComboBox()

        for resampling_mode in Image.Resampling.__members__:
            self._resampling_combo_box.addItem(resampling_mode.capitalize())

        resampling_layout = QHBoxLayout()
        resampling_layout.addWidget(resampling_label)
        resampling_layout.addStretch(stretch=1)
        resampling_layout.addWidget(self._resampling_combo_box)

        layout = QVBoxLayout()
        layout.addLayout(factor_layout)
        layout.addLayout(resampling_layout)

        self.setLayout(layout)

    @property
    def factor(self) -> int:
        return self._factor_spin_box.value()

    @property
    def resampling_mode(self) -> str:
        return self._resampling_combo_box.currentText()


class ParameterSlider(QWidget):
    def __init__(
        self,
        text: str,
        min_value: int,
        max_value: int,
        tick_interval: int | None = None,
        min_slider_width: int | None = None,
        min_spin_box_width: int | None = None,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        parent: QWidget | None = None,
        flags: Qt.WindowType | None = None,
    ) -> None:
        if flags is None:
            super().__init__(parent)
        else:
            super().__init__(parent, flags)

        label = QLabel(text)

        self._slider = QSlider(orientation)
        self._slider.setMinimum(min_value)
        self._slider.setMaximum(max_value)
        self._slider.valueChanged.connect(
            lambda: spin_box.setValue(self._slider.value())
        )

        if tick_interval is not None:
            self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            self._slider.setTickInterval(tick_interval)

        if min_slider_width is not None:
            self._slider.setMinimumWidth(min_slider_width)

        spin_box = QSpinBox()
        spin_box.setMinimum(min_value)
        spin_box.setMaximum(max_value)
        spin_box.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        spin_box.valueChanged.connect(lambda: self._slider.setValue(spin_box.value()))

        if min_spin_box_width is not None:
            spin_box.setMinimumWidth(min_spin_box_width)

        match orientation:
            case Qt.Orientation.Horizontal:
                layout = QHBoxLayout()
            case Qt.Orientation.Vertical:
                layout = QVBoxLayout()
            case _:
                layout = QHBoxLayout()

        layout.addWidget(label)

        if orientation is Qt.Orientation.Horizontal:
            layout.addStretch(1)

        layout.addWidget(self._slider)
        layout.addWidget(spin_box)

        self.setLayout(layout)

    @property
    def value(self) -> int:
        return self._slider.value()


class PreprocessingGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Preprocessing", parent)

        self._grayscale_check_box = QCheckBox("Grayscale conversion")

        self._brightness_slider = ParameterSlider(
            "Brightness:", -100, 100, tick_interval=50, min_slider_width=128
        )
        self._contrast_slider = ParameterSlider(
            "Contrast:", -100, 100, tick_interval=50, min_slider_width=128
        )

        layout = QVBoxLayout()
        layout.addWidget(self._grayscale_check_box)
        layout.addWidget(self._brightness_slider)
        layout.addWidget(self._contrast_slider)

        self.setLayout(layout)

    @property
    def grayscale(self) -> bool:
        return self._grayscale_check_box.isChecked()

    @property
    def brightness(self) -> int:
        return self._brightness_slider.value

    @property
    def contrast(self) -> int:
        return self._contrast_slider.value


class PaletteGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Color Palette", parent)

        self._palette_list_widget = QListWidget()

        self._add_button = QPushButton("Add")
        self._add_button.clicked.connect(self._add_color)

        self._edit_button = QPushButton("Edit")
        self._edit_button.clicked.connect(self._edit_color)

        self._remove_button = QPushButton("Remove")
        self._remove_button.clicked.connect(self._remove_color)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self._add_button)
        bottom_layout.addWidget(self._edit_button)
        bottom_layout.addWidget(self._remove_button)

        layout = QVBoxLayout()
        layout.addWidget(self._palette_list_widget)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    @property
    def num_colors(self) -> int:
        return self._palette_list_widget.count()

    def get_color_item(self, index: int) -> QListWidgetItem | None:
        return self._palette_list_widget.item(index)

    def _add_color(self) -> None:
        qcolor = QColorDialog.getColor()

        if qcolor.isValid():
            color = qcolor.getRgb()[:3]
            self._palette_list_widget.addItem(str(color))

    def _edit_color(self) -> None:
        selected_items = self._palette_list_widget.selectedItems()

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
        current_row = self._palette_list_widget.currentRow()
        self._palette_list_widget.takeItem(current_row)


class ParameterGroupBox(QGroupBox):
    def __init__(
        self,
        image_group_box: "ImageGroupBox",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Parameters", parent)

        self._image_group_box = image_group_box

        self._downsampling_group_box = DownsamplingGroupBox()
        self._preprocessing_group_box = PreprocessingGroupBox()
        self._palette_group_box = PaletteGroupBox()

        convert_button = QPushButton("Convert image")
        convert_button.clicked.connect(self._convert_image)

        layout = QVBoxLayout()
        layout.addWidget(self._downsampling_group_box)
        layout.addWidget(self._preprocessing_group_box)
        layout.addWidget(self._palette_group_box)
        layout.addStretch(stretch=1)
        layout.addWidget(convert_button)

        self.setLayout(layout)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        )

    def _convert_image(self) -> None:
        input_pixmap = self._image_group_box.input_pixmap

        if input_pixmap is None:
            return

        input_image = ImageQt.fromqpixmap(input_pixmap)

        downsampling_factor = self._downsampling_group_box.factor

        if downsampling_factor == 1:
            downsampling_factor = None

        resampling_mode_str = self._downsampling_group_box.resampling_mode
        resampling_mode = Image.Resampling[resampling_mode_str.upper()]

        enable_grayscale = self._preprocessing_group_box.grayscale
        brightness_adjustment = self._preprocessing_group_box.brightness / 100
        contrast_adjustment = self._preprocessing_group_box.contrast / 100

        colors: list[RGBColor] | None = []

        for color_index in range(self._palette_group_box.num_colors):
            color_item = self._palette_group_box.get_color_item(color_index)

            if color_item is not None:
                colors.append(ast.literal_eval(color_item.text()))

        if not colors:
            colors = None

        converted_image = convert_image(
            input_image,
            downsampling_factor=downsampling_factor,
            resampling_mode=resampling_mode,
            grayscale=enable_grayscale,
            brightness_adjustment=brightness_adjustment,
            contrast_adjustment=contrast_adjustment,
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

        self._image_group_box.set_output_pixmap(converted_image_pixmap)
        self._image_group_box.display_output_image()


class ImageLabel(QLabel):
    def __init__(
        self,
        pixmap: QPixmap | None = None,
        pixel_mode: bool = False,
        parent: QWidget | None = None,
        flags: Qt.WindowType | None = None,
    ) -> None:
        if flags is None:
            super().__init__(None, parent)
        else:
            super().__init__(None, parent, flags)

        self.true_pixmap = pixmap
        self._pixel_mode = pixel_mode

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_resized_pixmap()

    @override
    def resizeEvent(self, event: QResizeEvent) -> None:
        self._set_resized_pixmap()

    @override
    def setPixmap(self, pixmap: QPixmap) -> None:
        self.true_pixmap = pixmap
        self._set_resized_pixmap()

    def remove_pixmap(self):
        self.true_pixmap = None
        self.clear()

    def _set_resized_pixmap(self) -> None:
        if self.true_pixmap is not None:
            if self._pixel_mode:
                true_width = self.true_pixmap.height()
                true_height = self.true_pixmap.width()

                prescale_factor = max(
                    1, PIXEL_PRESCALE_FACTOR_BASE // min(true_width, true_height)
                )

                prescaled_pixmap = self.true_pixmap.scaled(
                    self.true_pixmap.size() * prescale_factor,
                    transformMode=Qt.TransformationMode.FastTransformation,
                )
            else:
                prescaled_pixmap = self.true_pixmap

            scaled_pixmap = prescaled_pixmap.scaled(
                self.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )

            super().setPixmap(scaled_pixmap)


class ImageGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Image (Empty)", parent)

        self._input_image_label = ImageLabel()
        self._output_image_label = ImageLabel(pixel_mode=True)

        self._image_label_stack = QStackedLayout()
        self._image_label_stack.addWidget(self._input_image_label)
        self._image_label_stack.addWidget(self._output_image_label)

        select_button = QPushButton("Select image...")
        select_button.clicked.connect(self._select_image)

        self._save_button = QPushButton("Save converted image...")
        self._save_button.clicked.connect(self._save_output)

        self._display_original_button = QPushButton("Display original")
        self._display_original_button.setCheckable(True)
        self._display_original_button.toggled.connect(self._on_display_toggle)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(select_button, stretch=1)
        buttons_layout.addWidget(self._save_button, stretch=1)
        buttons_layout.addWidget(
            self._display_original_button, alignment=Qt.AlignmentFlag.AlignTrailing
        )

        layout = QVBoxLayout()
        layout.addLayout(self._image_label_stack)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    @property
    def input_pixmap(self) -> QPixmap | None:
        return self._input_image_label.true_pixmap

    def set_output_pixmap(self, pixmap: QPixmap) -> None:
        self._output_image_label.setPixmap(pixmap)

    def display_output_image(self) -> None:
        self._image_label_stack.setCurrentWidget(self._output_image_label)
        self.setTitle("Converted Image")
        self._display_original_button.setChecked(False)

    def _on_display_toggle(self, checked: bool) -> None:
        if checked:
            if self._input_image_label.true_pixmap is not None:
                self._display_input_image()
        else:
            if self._output_image_label.true_pixmap is not None:
                self.display_output_image()

    def _display_input_image(self) -> None:
        self._image_label_stack.setCurrentWidget(self._input_image_label)
        self.setTitle("Original Image")

    def _select_image(self) -> None:
        file_path = QFileDialog.getOpenFileName()[0]

        if file_path == "":
            return

        self._input_image_label.setPixmap(QPixmap(file_path))
        self._output_image_label.remove_pixmap()
        self._display_input_image()

    def _save_output(self) -> None:
        output_pixmap = self._output_image_label.true_pixmap

        if output_pixmap is None:
            return

        file_path = QFileDialog.getSaveFileName(filter="Images (*.png *.jpg)")[0]

        if file_path == "":
            return

        output_image = ImageQt.fromqpixmap(output_pixmap)
        output_image.save(file_path)
