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

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget


class ImageField(QLabel):
    def __init__(
        self,
        pixmap: QPixmap | None = None,
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

        self.default_pixmap = pixmap
        self._transform_mode = transform_mode

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_resized_pixmap()

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.default_pixmap is not None:
            self.setPixmap(self.default_pixmap)

        super().resizeEvent(event)

    def _set_resized_pixmap(self) -> None:
        if self.default_pixmap is not None:
            scaled_pixmap = self.default_pixmap.scaled(
                self.size(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=self._transform_mode,
            )

            super().setPixmap(scaled_pixmap)

    def setPixmap(self, pixmap: QPixmap) -> None:
        self.default_pixmap = pixmap
        self._set_resized_pixmap()
