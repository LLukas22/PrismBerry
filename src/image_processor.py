from PIL import Image, ImageOps
from PIL.Image import Palette, Quantize, Dither
from models import BackgroundColor

PALETTE = (
    0,
    0,
    0,
    255,
    255,
    255,
    0,
    255,
    0,
    0,
    0,
    255,
    255,
    0,
    0,
    255,
    255,
    0,
    255,
    128,
    0,
) + (0, 0, 0) * 249


class ImageProcessor:
    def __init__(self, target_size: tuple[int, int] = (800, 480)):
        self.target_size = target_size
        self.color_image = Image.new("P", (1, 1))
        self.color_image.putpalette(PALETTE)

        self.gray_image = Image.new("P", (1, 1))
        self.gray_image.putpalette((0, 0, 0, 255, 255, 255) + (0, 0, 0) * 254)

    def __call__(
        self,
        image: Image,
        grayscale: bool = False,
        dither: bool = True,
        background_color: BackgroundColor = BackgroundColor.Black,
    ) -> Image:
        image = ImageOps.contain(image, self.target_size)

        palette = self.gray_image if grayscale else self.color_image
        quanitzed = image.convert("RGB").quantize(
            palette=palette,
            method=Quantize.FASTOCTREE,
            dither=Dither.FLOYDSTEINBERG if dither else Dither.NONE,
            kmeans=32,
        )

        left_padding = (self.target_size[0] - quanitzed.width) // 2
        top_padding = (self.target_size[1] - quanitzed.height) // 2
        right_padding = self.target_size[0] - quanitzed.width - left_padding
        bottom_padding = self.target_size[1] - quanitzed.height - top_padding

        # Pad the image
        quanitzed = ImageOps.expand(
            quanitzed,
            (left_padding, top_padding, right_padding, bottom_padding),
            fill=background_color.value,
        )
        return quanitzed
