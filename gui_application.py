import ast
import re
import sys

from PIL import Image, ImageQt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from source.conversion import convert_image
from source.typing import RGBColor

WINDOW_TITLE = "Pixel Art Palette Converter"
DEFAULT_COLORS = [
    (0, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 0),
    (255, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]


def main() -> None:
    app = QApplication(sys.argv)

    input_image_pixmap = QPixmap("resources/example-image.jpg")

    input_image_label = QLabel()
    input_image_label.setPixmap(input_image_pixmap)

    input_image_layout = QHBoxLayout()
    input_image_layout.addWidget(input_image_label)

    input_image_group_box = QGroupBox("Original Image")
    input_image_group_box.setLayout(input_image_layout)

    converted_image_label = QLabel()

    converted_image_layout = QHBoxLayout()
    converted_image_layout.addWidget(converted_image_label)

    converted_image_group_box = QGroupBox("Converted Image")
    converted_image_group_box.setLayout(converted_image_layout)

    default_colors_str = " ".join([str(color) for color in DEFAULT_COLORS])

    colors_option_label = QLabel("Colors:")

    colors_option_text_edit = QTextEdit()
    colors_option_text_edit.setText(default_colors_str)

    colors_option_layout = QVBoxLayout()
    colors_option_layout.addWidget(colors_option_label)
    colors_option_layout.addWidget(colors_option_text_edit)

    colors_option_widget = QWidget()
    colors_option_widget.setLayout(colors_option_layout)

    downsample_option_label = QLabel("Downsample factor:")

    downsample_option_spin_box = QSpinBox()
    downsample_option_spin_box.setMinimum(1)

    downsample_option_layout = QHBoxLayout()
    downsample_option_layout.addWidget(downsample_option_label)
    downsample_option_layout.addWidget(downsample_option_spin_box)

    downsample_option_widget = QWidget()
    downsample_option_widget.setLayout(downsample_option_layout)

    resampling_option_label = QLabel("Resampling mode:")

    resampling_option_combo_box = QComboBox()
    resampling_option_combo_box.addItem("Nearest")
    resampling_option_combo_box.addItem("Bicubic")

    resampling_option_layout = QHBoxLayout()
    resampling_option_layout.addWidget(resampling_option_label)
    resampling_option_layout.addWidget(resampling_option_combo_box)

    resampling_option_widget = QWidget()
    resampling_option_widget.setLayout(resampling_option_layout)

    def on_convert_image():
        input_image = ImageQt.fromqpixmap(input_image_pixmap)
        colors_str = colors_option_text_edit.toPlainText()
        colors = parse_colors_str(colors_str)
        downsample_factor = downsample_option_spin_box.value()
        resampling_mode_str = resampling_option_combo_box.currentText()

        match resampling_mode_str:
            case "Nearest":
                resampling_mode = Image.Resampling.NEAREST
            case "Bicubic":
                resampling_mode = Image.Resampling.BICUBIC
            case _:
                resampling_mode = Image.Resampling.NEAREST

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

        converted_image_label.setPixmap(converted_image_pixmap)

    convert_button = QPushButton("Convert Image")
    convert_button.clicked.connect(on_convert_image)

    options_layout = QVBoxLayout()
    options_layout.addWidget(colors_option_widget)
    options_layout.addWidget(downsample_option_widget)
    options_layout.addWidget(resampling_option_widget)
    options_layout.addWidget(convert_button)

    options_group_box = QGroupBox("Options")
    options_group_box.setLayout(options_layout)
    options_group_box.setSizePolicy(
        QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
    )

    central_layout = QHBoxLayout()
    central_layout.addWidget(input_image_group_box)
    central_layout.addWidget(converted_image_group_box)
    central_layout.addWidget(options_group_box)

    central_widget = QWidget()
    central_widget.setLayout(central_layout)

    window = QMainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    window.setCentralWidget(central_widget)
    window.show()

    app.exec()


def parse_colors_str(colors_str: str) -> list[RGBColor]:
    regex_pattern = r"\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)"
    regex_matches = re.findall(regex_pattern, colors_str)

    return [ast.literal_eval(tuple_str) for tuple_str in regex_matches]


if __name__ == "__main__":
    main()
