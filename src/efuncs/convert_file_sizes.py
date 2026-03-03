def convert_file_size(*, size: int | float, from_unit: str, to_unit: str) -> float:
    """
    Converts a file size from one unit to another.

    Args:
        size:      The numerical size value to convert.
        from_unit: The starting unit  ('B', 'KB', 'MB', 'GB', 'TB').
        to_unit:   The target unit    ('B', 'KB', 'MB', 'GB', 'TB').

    Returns:
        The converted file size as a float.

    Raises:
        ValueError: If size is negative or either unit is unrecognised.

    Examples:
        >>> convert_file_size(size=1, from_unit='GB', to_unit='MB')
        1024.0
        >>> convert_file_size(size=1024, from_unit='KB', to_unit='MB')
        1.0
    """
    BYTES_PER_UNIT = {
        'B':  1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }

    from_unit = from_unit.upper()
    to_unit   = to_unit.upper()

    valid_units = list(BYTES_PER_UNIT.keys())

    if size < 0:
        raise ValueError(f"size must be non-negative, got {size}.")
    if from_unit not in BYTES_PER_UNIT:
        raise ValueError(f"Invalid from_unit '{from_unit}'. Valid units: {valid_units}")
    if to_unit not in BYTES_PER_UNIT:
        raise ValueError(f"Invalid to_unit '{to_unit}'. Valid units: {valid_units}")

    return (size * BYTES_PER_UNIT[from_unit]) / BYTES_PER_UNIT[to_unit]
