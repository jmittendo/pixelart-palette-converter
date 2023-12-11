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
