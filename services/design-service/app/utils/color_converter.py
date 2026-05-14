from PIL import Image


def cmyk_to_rgb(c: float, m: float, y: float, k: float) -> tuple[int, int, int]:
    """Converts CMYK (0-1) to RGB (0-255)."""
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return int(r), int(g), int(b)


def convert_image_cmyk_to_rgb(image: Image.Image) -> Image.Image:
    """Converts PIL Image from CMYK to RGB."""
    if image.mode == "CMYK":
        return image.convert("RGB")
    return image
