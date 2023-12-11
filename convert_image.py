from argparse import ArgumentParser, Namespace
from pathlib import Path

from PIL import Image

from source.conversion import convert_image

COLORS = [
    (0, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 0),
    (255, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]
RESAMPLING_MODE = Image.Resampling.BICUBIC


def main() -> None:
    input_args = parse_input_args()
    image_file_path: Path | None = input_args.image_path
    downsample_factor: int | None = input_args.downsample_factor

    if image_file_path is None:
        image_file_path = Path(input("Enter image file path: "))

    if not image_file_path.is_file():
        raise FileNotFoundError(
            f"Could not find image file '{image_file_path.as_posix()}'"
        )

    if downsample_factor is None:
        user_input = input("Enter downsample factor (leave empty if none): ")

        if user_input in ("", "None"):
            downsample_factor = None
        else:
            downsample_factor = int(user_input)

    image = Image.open(image_file_path)

    converted_image = convert_image(
        image,
        colors=COLORS,
        downsample_factor=downsample_factor,
        resampling_mode=RESAMPLING_MODE,
    )

    output_path = image_file_path.with_name(f"{image_file_path.stem}_converted.png")

    converted_image.save(output_path)


def parse_input_args() -> Namespace:
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "image_path", nargs="?", type=Path, help="path to an image file"
    )
    arg_parser.add_argument(
        "-d",
        "--downsample",
        type=int,
        help="downsample factor (must be ≥1)",
        dest="downsample_factor",
    )

    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
