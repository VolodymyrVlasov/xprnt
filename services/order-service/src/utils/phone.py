import re

_UA_PHONE_RE = re.compile(r"^(\+?380|0)(\d{9})$")


def normalize_phone(phone: str) -> str:
    """
    Normalize Ukrainian phone number to +380XXXXXXXXX.
    Accepts: 0XXXXXXXXX, 380XXXXXXXXX, +380XXXXXXXXX.
    Raises ValueError on unrecognized format.
    """
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    m = _UA_PHONE_RE.match(cleaned)
    if not m:
        raise ValueError(f"Invalid Ukrainian phone number: {phone}")
    return f"+380{m.group(2)}"


def validate_phone(phone: str) -> bool:
    """Return True if phone is a valid Ukrainian number."""
    try:
        normalize_phone(phone)
        return True
    except ValueError:
        return False
