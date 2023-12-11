import numpy as np
from PIL import Image

from .typing import RGBColor


def convert_image(
    image: Image.Image,
    colors: list[RGBColor] | None = None,
    downsample_factor: int | None = None,
    resample_mode: Image.Resampling = Image.Resampling.NEAREST,
) -> Image.Image:
    if downsample_factor is not None:
        image = _downsample_image(image, downsample_factor, resample_mode)

    if colors is not None:
        image = _recolor_image(image, colors)

    return image


def _downsample_image(
    image: Image.Image, factor: int, resample_mode: Image.Resampling
) -> Image.Image:
    if factor < 1:
        raise ValueError("Downsample factor must not be smaller than 1")

    img_width, img_height = image.size

    new_width = img_width // factor
    new_height = img_height // factor

    return image.resize((new_width, new_height), resample=resample_mode)


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
