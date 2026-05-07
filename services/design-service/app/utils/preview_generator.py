import io
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


async def generate_preview(
    file_data: bytes,
    file_ext: str,
    max_size: tuple[int, int] = (1200, 1200),
) -> Optional[bytes]:
    """
    Generates a JPEG preview thumbnail.
    Returns None on failure (does not raise).
    """
    ext = file_ext.lower().lstrip(".")
    try:
        if ext in ("jpg", "jpeg", "png"):
            return _preview_from_raster(file_data, max_size)
        elif ext == "pdf":
            return await _preview_from_pdf(file_data, max_size)
        else:
            logger.warning("preview_generator: unsupported extension '%s'", ext)
            return None
    except Exception as exc:
        logger.error("generate_preview failed for ext='%s': %s", ext, exc)
        return None


def _preview_from_raster(file_data: bytes, max_size: tuple[int, int]) -> bytes:
    from PIL import Image

    from app.utils.color_converter import convert_image_cmyk_to_rgb

    img = Image.open(io.BytesIO(file_data))
    img = convert_image_cmyk_to_rgb(img)
    img.thumbnail(max_size)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


async def _preview_from_pdf(file_data: bytes, max_size: tuple[int, int]) -> bytes:
    from PIL import Image

    from app.utils.color_converter import convert_image_cmyk_to_rgb
    from app.utils.pdf_utils import render_pdf_first_page_to_image

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        img: Image.Image = render_pdf_first_page_to_image(tmp_path, dpi=150)
        img = convert_image_cmyk_to_rgb(img)
        img.thumbnail(max_size)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
