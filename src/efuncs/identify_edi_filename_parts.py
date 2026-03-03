import re
from dataclasses import dataclass
from typing import Optional

FILENAME_PART_NAMES = [
    'Project',
    'EDI',
    'FileDate',
    'FileTimestamp',
    'UniqueID',
    'FileDateRedundant',
    'FileTimestampRedundant',
    'FileExt',
    'Status',
]

EXPECTED_PART_COUNT = len(FILENAME_PART_NAMES)


@dataclass
class EdiFilenameParts:
    Project:                str
    EDI:                    str
    FileDate:               str
    FileTimestamp:          str
    UniqueID:               str
    FileDateRedundant:      str
    FileTimestampRedundant: str
    FileExt:                str
    Status:                 Optional[str] = None  # Not always present


def identify_edi_filename_parts(filename: str) -> EdiFilenameParts:
    """
    Parse an EDI filename into its component parts.

    Expected format:
        <Project>_<EDI>_<FileDate>_<FileTimestamp>_<UniqueID>_<FileDateRedundant>_<FileTimestampRedundant>.<FileExt>[.<Status>]

    Example:
        dteb_214a_20230101_120000_000001_20230101_120000.edi.completed
        -> Project='dteb', EDI='214a', FileDate='20230101', ...

    Raises:
        ValueError: If the filename cannot be parsed into the expected number of parts.
    """
    parts = re.split(r'[_.]', filename)

    if len(parts) not in (EXPECTED_PART_COUNT, EXPECTED_PART_COUNT - 1):
        raise ValueError(
            f"Filename '{filename}' produced {len(parts)} parts; "
            f"expected {EXPECTED_PART_COUNT - 1} or {EXPECTED_PART_COUNT}. "
            f"Parts found: {parts}"
        )

    # Pad with None if Status is absent
    if len(parts) == EXPECTED_PART_COUNT - 1:
        parts.append(None)

    return EdiFilenameParts(**dict(zip(FILENAME_PART_NAMES, parts)))
