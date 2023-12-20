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

from typing import override

from PIL import Image, ImageQt
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QImage,
    QKeySequence,
    QPainter,
    QPixmap,
    QResizeEvent,
    QStandardItem,
    QStandardItemModel,
)
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from source.conversion import convert_image
from source.typing import RGBColor

PIXEL_PRESCALE_FACTOR_BASE = 4096


class MainWindow(QMainWindow):
    def __init__(
        self,
        title: str,
        icon: QIcon,
        min_size: tuple[int, int],
        parent: QWidget | None = None,
        flags: Qt.WindowType | None = None,
    ) -> None:
        if flags is None:
            super().__init__(parent)
        else:
            super().__init__(parent, flags)

        gui = GUI()

        open_action = QAction("Open image...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(gui.open_image)

        save_action = QAction("Save converted image", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(gui.save_image)

        save_as_action = QAction("Save converted image as...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(gui.save_image_as)

        exit_action = QAction("Close", self)
        exit_action.triggered.connect(self.close)

        menu_bar = self.menuBar()

        if menu_bar is not None:
            file_menu = menu_bar.addMenu("File")

            if file_menu is not None:
                file_menu.addAction(open_action)
                file_menu.addAction(save_action)
                file_menu.addAction(save_as_action)
                file_menu.addAction(exit_action)

        self.setWindowTitle(title)
        self.setWindowIcon(icon)
        self.setMinimumSize(*min_size)
        self.setCentralWidget(gui)


class GUI(QWidget):
    def __init__(
        self, parent: QWidget | None = None, flags: Qt.WindowType | None = None
    ) -> None:
        if flags is None:
            super().__init__(parent)
        else:
            super().__init__(parent, flags)

        self._image_group_box = ImageGroupBox()
        parameter_group_box = ParameterGroupBox(self._image_group_box)

        layout = QHBoxLayout()
        layout.addWidget(parameter_group_box, stretch=1)
        layout.addWidget(self._image_group_box, stretch=1)

        self.setLayout(layout)

    def open_image(self) -> None:
        self._image_group_box.open_image()

    def save_image(self) -> None:
        self._image_group_box.save_output()

    def save_image_as(self) -> None:
        self._image_group_box.save_output_as()


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


class ColorItem(QStandardItem):
    def __init__(self, color: RGBColor) -> None:
        super().__init__()

        self.set_color(color)
        self.setEditable(False)

    @property
    def color(self) -> RGBColor:
        return self.data()

    def set_color(self, color: RGBColor) -> None:
        self._update(color)

    def _update(self, color: RGBColor) -> None:
        self.setData(color)
        self.setIcon(self._get_icon(color))

        hex_text = "#" + "".join(f"{value:02x}" for value in color)
        self.setText(f"{hex_text} {str(color)}")

    def _get_icon(self, color: RGBColor) -> QIcon:
        pixmap = QPixmap(16, 16)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(*color))
        painter.drawRect(pixmap.rect())
        painter.end()

        return QIcon(pixmap)


class PaletteGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Color Palette", parent)

        self._color_items_model = QStandardItemModel()

        self._color_items_view = QListView()
        self._color_items_view.setModel(self._color_items_model)

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
        layout.addWidget(self._color_items_view)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    @property
    def colors(self) -> list[RGBColor]:
        colors: list[RGBColor] = []

        for index in range(self._color_items_model.rowCount()):
            color_item = self._color_items_model.item(index)

            if color_item is not None:
                colors.append(color_item.data())

        return colors

    def _add_color(self) -> None:
        qcolor = QColorDialog.getColor()

        if qcolor.isValid():
            color = qcolor.getRgb()[:3]
            color_item = ColorItem(color)  # type: ignore

            self._color_items_model.appendRow(color_item)

    def _edit_color(self) -> None:
        color_items = self._get_selected_color_items()

        for color_item in color_items:
            current_color = color_item.color
            current_qcolor = QColor(*current_color)
            new_qcolor = QColorDialog.getColor(initial=current_qcolor)

            if new_qcolor.isValid():
                new_color = new_qcolor.getRgb()[:3]
                color_item.set_color(new_color)  # type: ignore

    def _remove_color(self) -> None:
        color_items = self._get_selected_color_items()

        for color_item in color_items:
            self._color_items_model.takeRow(color_item.row())

    def _get_selected_color_items(self) -> list[ColorItem]:
        selected_indices = self._color_items_view.selectedIndexes()

        selected_items: list[ColorItem] = []

        for index in selected_indices:
            color_item: ColorItem = self._color_items_model.itemFromIndex(index)  # type: ignore

            if color_item is not None:
                selected_items.append(color_item)

        return selected_items


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

        colors: list[RGBColor] | None = self._palette_group_box.colors

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

    def remove_pixmap(self) -> None:
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


class ImageLabelStack(QStackedWidget):
    image_dropped = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        empty_label = QLabel("Drag and drop image here...")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        super().addWidget(empty_label)

        self.setAcceptDrops(True)

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime_data = event.mimeData()

        if mime_data is not None and mime_data.hasUrls():
            event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        mime_data = event.mimeData()

        if mime_data is not None:
            file_path = mime_data.urls()[0].toLocalFile()

            self.image_dropped.emit(file_path)

    @override
    def addWidget(self, widget: QWidget | None = None) -> int:
        if not isinstance(widget, ImageLabel):
            raise TypeError("Can only add widgets of type ImageLabel")

        return self.add_image_label(widget)

    def add_image_label(self, image_label: ImageLabel) -> int:
        return super().addWidget(image_label)


class ImageGroupBox(QGroupBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Image (Empty)", parent)

        self._output_file_path: str | None = None

        self._input_image_label = ImageLabel()
        self._output_image_label = ImageLabel(pixel_mode=True)

        self._image_label_stack = ImageLabelStack()
        self._image_label_stack.add_image_label(self._input_image_label)
        self._image_label_stack.add_image_label(self._output_image_label)
        self._image_label_stack.image_dropped.connect(self._load_image)

        self._show_original_button = QPushButton("Show original")
        self._show_original_button.setCheckable(True)
        self._show_original_button.toggled.connect(self._on_display_toggle)

        layout = QVBoxLayout()
        layout.addWidget(self._image_label_stack)
        layout.addWidget(
            self._show_original_button, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.setLayout(layout)

    @property
    def input_pixmap(self) -> QPixmap | None:
        return self._input_image_label.true_pixmap

    def set_output_pixmap(self, pixmap: QPixmap) -> None:
        self._output_image_label.setPixmap(pixmap)

    def display_output_image(self) -> None:
        self._image_label_stack.setCurrentWidget(self._output_image_label)
        self.setTitle("Converted Image")
        self._show_original_button.setChecked(False)

    def open_image(self) -> None:
        file_path = QFileDialog.getOpenFileName()[0]

        if file_path == "":
            return

        self._load_image(file_path)

    def save_output(self) -> None:
        if self._output_file_path is None:
            self.save_output_as()
        else:
            output_pixmap = self._output_image_label.true_pixmap

            if output_pixmap is None:
                return

            self._save_output_pixmap(output_pixmap, self._output_file_path)

    def save_output_as(self) -> None:
        output_pixmap = self._output_image_label.true_pixmap

        if output_pixmap is None:
            return

        file_path = QFileDialog.getSaveFileName(filter="Images (*.png *.jpg)")[0]

        if file_path == "":
            return

        self._save_output_pixmap(output_pixmap, file_path)
        self._output_file_path = file_path

    def _save_output_pixmap(self, output_pixmap: QPixmap, file_path: str) -> None:
        output_image = ImageQt.fromqpixmap(output_pixmap)
        output_image.save(file_path)

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

    def _load_image(self, file_path: str) -> None:
        self._input_image_label.setPixmap(QPixmap(file_path))
        self._output_image_label.remove_pixmap()
        self._display_input_image()
        self._output_file_path = None
