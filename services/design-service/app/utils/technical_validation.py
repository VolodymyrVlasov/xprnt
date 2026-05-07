import io
import logging
from typing import Optional

from app.schemas.design import CurrentMetadata, DesignMetadata, MetadataField, TargetMetadata

logger = logging.getLogger(__name__)


def validate_design_metadata(
    file_data: bytes,
    file_ext: str,
    target_dpi: int,
    target_width_mm: Optional[float],
    target_height_mm: Optional[float],
    target_color: str,
) -> DesignMetadata:
    """
    Validates file and returns DesignMetadata with current and target fields.
    Does not crash on errors — returns isValid=False with value=None on failure.
    """
    ext = file_ext.lower().lstrip(".")

    target = TargetMetadata(
        dpi=target_dpi,
        width=target_width_mm,
        height=target_height_mm,
        color=target_color,
    )

    if ext in ("jpg", "jpeg", "png"):
        current = _validate_raster(file_data, ext, target_dpi, target_width_mm, target_height_mm, target_color)
    elif ext == "pdf":
        current = _validate_pdf(file_data, target_width_mm, target_height_mm, target_color)
    else:
        current = _unknown_current()

    return DesignMetadata(current=current, target=target)


# ── raster ─────────────────────────────────────────────────────────────────

def _validate_raster(
    file_data: bytes,
    ext: str,
    target_dpi: int,
    target_width_mm: Optional[float],
    target_height_mm: Optional[float],
    target_color: str,
) -> CurrentMetadata:
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(file_data))
        img_dpi_info = img.info.get("dpi", None)

        if img_dpi_info:
            dpi_val = round(float(img_dpi_info[0]))
        else:
            dpi_val = 72

        width_px, height_px = img.size
        width_mm = round(width_px / dpi_val * 25.4, 1)
        height_mm = round(height_px / dpi_val * 25.4, 1)

        color_val = "cmyk" if img.mode == "CMYK" else "rgb"

        dpi_valid = dpi_val == target_dpi
        width_valid = True if target_width_mm is None else abs(width_mm - target_width_mm) <= 1.0
        height_valid = True if target_height_mm is None else abs(height_mm - target_height_mm) <= 1.0
        color_valid = color_val == target_color

        return CurrentMetadata(
            dpi=MetadataField(value=dpi_val, isValid=dpi_valid),
            width=MetadataField(value=width_mm, isValid=width_valid),
            height=MetadataField(value=height_mm, isValid=height_valid),
            color=MetadataField(value=color_val, isValid=color_valid),
        )
    except Exception as exc:
        logger.warning("Raster metadata validation failed: %s", exc)
        return _error_current(target_width_mm, target_height_mm, target_color)


# ── pdf ────────────────────────────────────────────────────────────────────

def _validate_pdf(
    file_data: bytes,
    target_width_mm: Optional[float],
    target_height_mm: Optional[float],
    target_color: str,
) -> CurrentMetadata:
    import tempfile, os

    tmp_path = None
    try:
        from app.utils.pdf_utils import get_pdf_color_model, get_pdf_page_size_mm

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name

        width_mm, height_mm = get_pdf_page_size_mm(tmp_path)
        color_val = get_pdf_color_model(tmp_path)

        width_valid = True if target_width_mm is None else abs(width_mm - target_width_mm) <= 1.0
        height_valid = True if target_height_mm is None else abs(height_mm - target_height_mm) <= 1.0
        color_valid = color_val == target_color

        return CurrentMetadata(
            dpi=MetadataField(value=None, isValid=True),  # N/A for PDF
            width=MetadataField(value=width_mm, isValid=width_valid),
            height=MetadataField(value=height_mm, isValid=height_valid),
            color=MetadataField(value=color_val, isValid=color_valid),
        )
    except Exception as exc:
        logger.warning("PDF metadata validation failed: %s", exc)
        return _error_current(target_width_mm, target_height_mm, target_color)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── helpers ────────────────────────────────────────────────────────────────

def _unknown_current() -> CurrentMetadata:
    return CurrentMetadata(
        dpi=MetadataField(value=None, isValid=False),
        width=MetadataField(value=None, isValid=False),
        height=MetadataField(value=None, isValid=False),
        color=MetadataField(value=None, isValid=False),
    )


def _error_current(
    target_width_mm: Optional[float],
    target_height_mm: Optional[float],
    target_color: str,
) -> CurrentMetadata:
    return CurrentMetadata(
        dpi=MetadataField(value=None, isValid=False),
        width=MetadataField(value=None, isValid=False),
        height=MetadataField(value=None, isValid=False),
        color=MetadataField(value=None, isValid=False),
    )
