"""
Name normalization and standardization for rider matching.

This module provides consistent name handling across all VeloPredict components.
"""
import pandas as pd


# Known name corrections for data quality issues (typos in source data)
# Maps incorrect standardized name -> correct standardized name
NAME_CORRECTIONS = {
    # Men Elite - typos found in source data
    "niels vanputte": "niels vandeputte",
    "michael vanhourenhout": "michael vanthourenhout",
    "mees hendrixx": "mees hendrikx",
    "remi lelannais": "remi lelandais",
    # Add more corrections as discovered
}


def normalize_name(name: str) -> str | None:
    """
    Normalize rider name by removing diacritics and converting to lowercase.

    Args:
        name: Raw rider name

    Returns:
        Normalized name (lowercase, no diacritics) or None if input is invalid
    """
    if pd.isna(name):
        return None
    name = str(name).strip().lower()
    name = (
        name.replace("é", "e").replace("è", "e").replace("ë", "e")
            .replace("ó", "o").replace("ò", "o").replace("ö", "o")
            .replace("á", "a").replace("à", "a").replace("ä", "a")
            .replace("ü", "u").replace("ï", "i").replace("ř", "r")
            .replace("ž", "z").replace("š", "s").replace("č", "c")
            .replace("ý", "y").replace("í", "i").replace("ň", "n")
            .replace("ě", "e").replace("ď", "d").replace("ť", "t")
            .replace("ç", "c").replace("ñ", "n").replace("ø", "o")
    )
    return name


def standardize_name(s: str) -> str | None:
    """
    Standardize name to 'firstname lastname' format for consistent matching.

    Handles:
    - 'LASTNAME Firstname' -> 'firstname lastname'
    - 'VAN ALPHEN Aniek' -> 'aniek van alphen' (multi-word last names)
    - 'Firstname Lastname' -> 'firstname lastname'
    - Known typos/misspellings via NAME_CORRECTIONS

    Args:
        s: Input name in any format

    Returns:
        Standardized name in 'firstname lastname' format, or None if invalid
    """
    if pd.isna(s):
        return None
    s = str(s).strip()

    # Remove diacritics for matching
    normalized = normalize_name(s)
    if normalized is None:
        return None

    parts = normalized.split()
    orig_parts = s.split()

    if len(parts) < 2:
        result = normalized
    else:
        # Find where the uppercase last name ends and firstname begins
        # E.g., "VAN ALPHEN Aniek" - find index of first non-uppercase word
        first_lower_idx = None
        for i, p in enumerate(orig_parts):
            if not p.isupper():
                first_lower_idx = i
                break

        if first_lower_idx is not None and first_lower_idx > 0:
            # Found pattern like "VAN ALPHEN Aniek" or "LASTNAME Firstname"
            first_name_parts = parts[first_lower_idx:]
            last_name_parts = parts[:first_lower_idx]
            result = f"{' '.join(first_name_parts)} {' '.join(last_name_parts)}"
        elif all(p.isupper() for p in orig_parts):
            # All uppercase: "LASTNAME FIRSTNAME" -> assume first word is last name
            result = f"{parts[1]} {parts[0]}"
        else:
            # Default: already in firstname lastname format
            result = normalized

    # Apply known name corrections for data quality issues
    return NAME_CORRECTIONS.get(result, result)
