"""Unicode-safe BOQ unit validation and canonicalization."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

MAX_UNIT_LENGTH = 24
ALLOWED_UNIT_PUNCTUATION = frozenset("._/%-^ ")


def is_valid_unit(value: Any) -> bool:
    """Accept compact Arabic or English engineering-unit labels."""

    if not isinstance(value, str):
        return False
    candidate = value.strip()
    if not candidate or len(candidate) > MAX_UNIT_LENGTH:
        return False
    return all(character.isalnum() or character in ALLOWED_UNIT_PUNCTUATION for character in candidate)


def _alias_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[\s._\-/^]+", "", normalized)


_CANONICAL_ALIASES = {
    "m": {"m", "meter", "metre", "م"},
    "m2": {"m2", "m²", "m^2", "sqm", "sq.m", "م2", "م²", "م^2"},
    "m3": {"m3", "m³", "m^3", "cum", "cu.m", "م3", "م³", "م^3"},
    "no": {"no", "nos", "nr", "number", "each", "ea", "عدد"},
    "kg": {"kg", "kgs", "kilogram", "kilograms", "كجم", "كغ", "كيلوجرام"},
    "t": {"t", "ton", "tons", "tonne", "tonnes", "طن"},
    "ls": {"ls", "l.s", "lump sum", "lumpsum", "مقطوعية", "مقطوعيه"},
}
_ALIAS_TO_CANONICAL = {
    _alias_key(alias): canonical
    for canonical, aliases in _CANONICAL_ALIASES.items()
    for alias in aliases
}


def normalize_unit(value: Any) -> str | None:
    """Return a canonical value without changing the displayed source unit."""

    if not isinstance(value, str) or not value.strip():
        return None
    candidate = unicodedata.normalize("NFKC", value).strip()
    return _ALIAS_TO_CANONICAL.get(_alias_key(candidate), candidate.casefold())
