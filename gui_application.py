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

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from source.gui import GUI

WINDOW_TITLE = "Pixel Art Palette Converter"
MINIMUM_WINDOW_SIZE = (1280, 540)


def main() -> None:
    app = QApplication(sys.argv)
    gui = GUI()

    window = QMainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    window.setMinimumSize(*MINIMUM_WINDOW_SIZE)
    window.setCentralWidget(gui)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
