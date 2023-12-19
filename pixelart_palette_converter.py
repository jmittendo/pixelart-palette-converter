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

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from source.gui import MainWindow

WINDOW_TITLE = "Pixel Art Palette Converter"
ICON_PATH = "resources/icon.png"
MINIMUM_WINDOW_SIZE = (960, 540)


def main() -> None:
    app = QApplication(sys.argv)

    window = MainWindow(WINDOW_TITLE, QIcon(ICON_PATH), MINIMUM_WINDOW_SIZE)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
