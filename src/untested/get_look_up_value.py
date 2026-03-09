def get_lookup_value(
    lookup_key: str,
    table: dict,
    segment_element: str = None,
    *,
    include_lookup_key: bool = True,
    include_ref_source: bool = False,
    include_segment_element: bool = False,
) -> str:
    """
    Look up a value from a reference table and return it with optional suffix tags.

    Args:
        lookup_key:              The key to look up in the table.
        table:                   A dictionary to look up from (see examples below).
        segment_element:         Optional segment element appended as a tag.
        include_lookup_key:      Append the lookup key as a tag e.g. (ZZ).
        include_ref_source:      Append the source as a tag e.g. (DTEB).
        include_segment_element: Append the segment element as a tag e.g. (BN402).

    Returns:
        The lookup value with any requested suffix tags.

    Examples:
        >>> get_lookup_value("ZZ", {"ZZ": "Some Value"}, "BN402",
        ...                  include_lookup_key=True, include_ref_source=True,
        ...                  include_segment_element=True)
        'Some Value (ZZ)(DTEB)(BN402)'

        >>> get_lookup_value("XX", {"ZZ": "Some Value"}, include_lookup_key=False)
        'Unknown Value'
    """
    lookup_value = table.get(str(lookup_key), "Unknown Value")
    source = "DTEB"

    tags = []
    if include_lookup_key:       tags.append(f"({lookup_key})")
    if include_ref_source:       tags.append(f"({source})")
    if include_segment_element:  tags.append(f"({segment_element})")

    suffix = (" " + "".join(tags)) if tags else ""
    return f"{lookup_value}{suffix}"


import doctest
doctest.testmod()
