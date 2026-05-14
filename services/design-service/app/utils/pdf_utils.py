import logging

from PIL import Image

logger = logging.getLogger(__name__)


def get_pdf_page_size_mm(pdf_path: str) -> tuple[float, float]:
    """Returns the size of the first PDF page in mm."""
    try:
        import pypdf

        reader = pypdf.PdfReader(pdf_path)
        page = reader.pages[0]
        # MediaBox values are in points (1 pt = 25.4/72 mm)
        width_pt = float(page.mediabox.width)
        height_pt = float(page.mediabox.height)
        width_mm = round(width_pt * 25.4 / 72, 1)
        height_mm = round(height_pt * 25.4 / 72, 1)
        return width_mm, height_mm
    except Exception as exc:
        logger.warning("get_pdf_page_size_mm failed: %s", exc)
        return 0.0, 0.0


def get_pdf_color_model(pdf_path: str) -> str:
    """
    Detects the color model of a PDF (cmyk / rgb / unknown).
    Analyses the colorspace resources of the first page.
    """
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            # pdfplumber exposes the raw PDF object
            resources = page.page_obj.get("/Resources", {})
            colorspace = resources.get("/ColorSpace", {})
            cs_values = list(colorspace.values()) if colorspace else []
            cs_str = str(cs_values).lower()
            if "cmyk" in cs_str or "devicecmyk" in cs_str:
                return "cmyk"
            if "rgb" in cs_str or "devicergb" in cs_str:
                return "rgb"
            # Fall back to checking the page content stream for colour ops
            content = page.page_obj.get("/Contents", None)
            if content:
                raw = content.get_data() if hasattr(content, "get_data") else b""
                raw_str = raw.decode("latin-1", errors="ignore").lower()
                if "k " in raw_str or " k\n" in raw_str:  # CMYK fill/stroke ops
                    return "cmyk"
                if "rg " in raw_str or " rg\n" in raw_str:
                    return "rgb"
    except Exception as exc:
        logger.warning("get_pdf_color_model failed: %s", exc)
    return "unknown"


def render_pdf_first_page_to_image(pdf_path: str, dpi: int = 150) -> Image.Image:
    """Renders the first page of a PDF to a PIL Image using pdf2image (poppler)."""
    from pdf2image import convert_from_path

    images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
    return images[0]
