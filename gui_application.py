import ast
import sys

from PIL import Image, ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from source.conversion import convert_image
from source.gui import ImageField
from source.typing import RGBColor

WINDOW_TITLE = "Pixel Art Palette Converter"
MINIMUM_WINDOW_SIZE = (1280, 540)


def main() -> None:
    app = QApplication(sys.argv)

    colors_option_label = QLabel("Colors:")
    colors_option_list_widget = QListWidget()

    def on_add_color() -> None:
        qcolor = QColorDialog.getColor()

        if qcolor.isValid():
            color = qcolor.getRgb()[:3]
            colors_option_list_widget.addItem(str(color))

    def on_edit_color() -> None:
        selected_items = colors_option_list_widget.selectedItems()

        if not selected_items:
            return

        selected_item = selected_items[0]

        current_color = ast.literal_eval(selected_item.text())
        current_qcolor = QColor(*current_color)

        new_qcolor = QColorDialog.getColor(initial=current_qcolor)

        if new_qcolor.isValid():
            new_color = new_qcolor.getRgb()[:3]
            selected_item.setText(str(new_color))

    def on_remove_color() -> None:
        current_row = colors_option_list_widget.currentRow()
        colors_option_list_widget.takeItem(current_row)

    colors_option_add_button = QPushButton("Add")
    colors_option_add_button.clicked.connect(on_add_color)

    colors_option_edit_button = QPushButton("Edit")
    colors_option_edit_button.clicked.connect(on_edit_color)

    colors_option_remove_button = QPushButton("Remove")
    colors_option_remove_button.clicked.connect(on_remove_color)

    colors_option_bottom_layout = QHBoxLayout()
    colors_option_bottom_layout.addWidget(colors_option_add_button)
    colors_option_bottom_layout.addWidget(colors_option_edit_button)
    colors_option_bottom_layout.addWidget(colors_option_remove_button)

    colors_option_layout = QVBoxLayout()
    colors_option_layout.addWidget(colors_option_label)
    colors_option_layout.addWidget(colors_option_list_widget)
    colors_option_layout.addLayout(colors_option_bottom_layout)

    colors_option_widget = QWidget()
    colors_option_widget.setLayout(colors_option_layout)

    downsample_option_label = QLabel("Downsample factor:")

    downsample_option_spin_box = QSpinBox()
    downsample_option_spin_box.setMinimum(1)

    downsample_option_layout = QHBoxLayout()
    downsample_option_layout.addWidget(downsample_option_label)
    downsample_option_layout.addStretch(stretch=1)
    downsample_option_layout.addWidget(downsample_option_spin_box)

    downsample_option_widget = QWidget()
    downsample_option_widget.setLayout(downsample_option_layout)

    resampling_option_label = QLabel("Resampling mode:")

    resampling_option_combo_box = QComboBox()

    for resampling_mode in Image.Resampling.__members__:
        resampling_option_combo_box.addItem(resampling_mode.capitalize())

    resampling_option_layout = QHBoxLayout()
    resampling_option_layout.addWidget(resampling_option_label)
    resampling_option_layout.addStretch(stretch=1)
    resampling_option_layout.addWidget(resampling_option_combo_box)

    resampling_option_widget = QWidget()
    resampling_option_widget.setLayout(resampling_option_layout)

    def on_convert_image() -> None:
        input_image = ImageQt.fromqpixmap(input_image_pixmap)

        colors: list[RGBColor] | None = []

        for item_index in range(colors_option_list_widget.count()):
            item = colors_option_list_widget.item(item_index)

            if item is not None:
                colors.append(ast.literal_eval(item.text()))

        if not colors:
            colors = None

        downsample_factor = downsample_option_spin_box.value()

        if downsample_factor == 1:
            downsample_factor = None

        resampling_mode_str = resampling_option_combo_box.currentText()
        resampling_mode = Image.Resampling[resampling_mode_str.upper()]

        converted_image = convert_image(
            input_image,
            colors=colors,
            downsample_factor=downsample_factor,
            resampling_mode=resampling_mode,
        )
        converted_qimage = QImage(
            converted_image.tobytes(),
            converted_image.width,
            converted_image.height,
            converted_image.width * 3,
            QImage.Format.Format_RGB888,
        )
        converted_image_pixmap = QPixmap(converted_qimage)

        converted_image_field.setPixmap(converted_image_pixmap)

    convert_button = QPushButton("Convert Image")
    convert_button.clicked.connect(on_convert_image)

    options_layout = QVBoxLayout()
    options_layout.addWidget(colors_option_widget)
    options_layout.addWidget(downsample_option_widget)
    options_layout.addWidget(resampling_option_widget)
    options_layout.addStretch(stretch=1)
    options_layout.addWidget(convert_button)

    options_group_box = QGroupBox("Options")
    options_group_box.setLayout(options_layout)
    options_group_box.setSizePolicy(
        QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
    )

    input_image_pixmap = QPixmap("resources/example-image.jpg")
    input_image_field = ImageField(input_image_pixmap)

    input_image_layout = QHBoxLayout()
    input_image_layout.addWidget(input_image_field)

    input_image_group_box = QGroupBox("Original Image")
    input_image_group_box.setLayout(input_image_layout)

    converted_image_field = ImageField(
        transform_mode=Qt.TransformationMode.FastTransformation
    )

    converted_image_layout = QHBoxLayout()
    converted_image_layout.addWidget(converted_image_field)

    converted_image_group_box = QGroupBox("Converted Image")
    converted_image_group_box.setLayout(converted_image_layout)

    central_layout = QHBoxLayout()
    central_layout.addWidget(options_group_box, stretch=1)
    central_layout.addWidget(input_image_group_box, stretch=1)
    central_layout.addWidget(converted_image_group_box, stretch=1)

    central_widget = QWidget()
    central_widget.setLayout(central_layout)
    central_widget.setMinimumSize(*MINIMUM_WINDOW_SIZE)

    window = QMainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    window.setCentralWidget(central_widget)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
