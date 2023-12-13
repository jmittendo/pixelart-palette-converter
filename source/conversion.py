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

import numpy as np
from PIL import Image

from .typing import RGBColor


def convert_image(
    image: Image.Image,
    downsampling_factor: int | None = None,
    resampling_mode: Image.Resampling = Image.Resampling.NEAREST,
    grayscale: bool = False,
    brightness_adjustment: float = 0,
    contrast_adjustment: float = 0,
    colors: list[RGBColor] | None = None,
) -> Image.Image:
    if downsampling_factor is not None:
        image = _downsample_image(image, downsampling_factor, resampling_mode)

    if grayscale:
        image = image.convert("L").convert("RGB")

    if brightness_adjustment != 0 or contrast_adjustment != 0:
        image = _adjust_brightness_and_contrast(
            image, brightness_adjustment, contrast_adjustment
        )

    if colors is not None:
        image = _recolor_image(image, colors)

    return image


def _downsample_image(
    image: Image.Image, factor: int, resampling_mode: Image.Resampling
) -> Image.Image:
    if factor < 1:
        raise ValueError("Downsampling factor must not be smaller than 1")

    img_width, img_height = image.size

    new_width = img_width // factor
    new_height = img_height // factor

    return image.resize((new_width, new_height), resample=resampling_mode)


def _adjust_brightness_and_contrast(
    image: Image.Image, brightness_adjustment: float, contrast_adjustment: float
) -> Image.Image:
    # Algorithm adapted from GIMP (GNU Image Manipulation Program):
    # https://github.com/GNOME/gimp/blob/master/app/operations/gimpoperationbrightnesscontrast.c

    image_array = np.asarray(image) / 255

    if brightness_adjustment == 0:
        pass
    elif brightness_adjustment < 0:
        image_array *= 1 + 0.5 * brightness_adjustment
    else:
        image_array = image_array + (1 - image_array) * 0.5 * brightness_adjustment

    if contrast_adjustment != 0:
        contrast_factor = np.tan(0.25 * (1 + contrast_adjustment) * np.pi)
        image_array = (image_array - 0.5) * contrast_factor + 0.5

    image_array = (image_array.clip(min=0, max=1) * 255).astype(np.uint8)

    return Image.fromarray(image_array)


def _recolor_image(image: Image.Image, colors: list[RGBColor]) -> Image.Image:
    image_array = np.asarray(image)

    # Alpha channel workaround
    if image_array.shape[-1] == 4:
        image_array = image_array[:, :, :3]

    colors_array = np.asarray(colors)
    rgb_difference_vectors = image_array[:, :, np.newaxis, :] - colors_array
    rgb_distances = np.linalg.norm(rgb_difference_vectors, axis=-1)
    closest_color_indices = rgb_distances.argmin(axis=-1)
    new_image_array = colors_array[closest_color_indices].astype(np.uint8)

    return Image.fromarray(new_image_array)
