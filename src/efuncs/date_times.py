from datetime import datetime


def parse_date(date_str: str) -> datetime:
    '''
    Parse a date string into a Python datetime object.

    Supported formats, detected automatically:
        YYMMDD          (6 digits)   — 2-digit year; 00-68 → 2000-2068,
                                       69-99 → 1969-1999
        CCYYMMDD        (8 digits)   — 4-digit century year, no separators
        YYYY-MM-DD      (10 chars)   — ISO 8601 with hyphens
        YYYY/MM/DD      (10 chars)   — slash-separated
        MM/DD/YYYY      (10 chars)   — US format with slashes
        MM-DD-YYYY      (10 chars)   — US format with hyphens

    Parameters
    ----------
    date_str : str
        Date string in any of the supported formats.

    Returns
    -------
    datetime
        datetime object with time components set to midnight (00:00:00).

    Raises
    ------
    ValueError
        If the string does not match any supported format or is not a valid date.

    Examples
    --------
    >>> parse_date('20060101')
    datetime.datetime(2006, 1, 1, 0, 0)

    >>> parse_date('2006-01-01')
    datetime.datetime(2006, 1, 1, 0, 0)

    >>> parse_date('01/01/2006')
    datetime.datetime(2006, 1, 1, 0, 0)
    '''
    date_str = date_str.strip()

    if date_str.isdigit():
        formats = {
            6: '%y%m%d',
            8: '%Y%m%d',
        }
        fmt = formats.get(len(date_str))
        if not fmt:
            raise ValueError(
                f"Unrecognized compact date format: '{date_str}'. "
                f"Expected YYMMDD (6 digits) or CCYYMMDD (8 digits), "
                f"got {len(date_str)} digits."
            )
        return datetime.strptime(date_str, fmt)

    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%m-%d-%Y']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Unrecognized date format: '{date_str}'. "
        f"Supported formats: YYMMDD, CCYYMMDD, YYYY-MM-DD, YYYY/MM/DD, "
        f"MM/DD/YYYY, MM-DD-YYYY."
    )


def parse_time(time_str: str) -> datetime:
    '''
    Parse a time string into a Python datetime object.

    Supported formats (all 24-hour clock):
        HHMM        (4 digits)  — hours and minutes
        HHMMSS      (6 digits)  — hours, minutes, seconds
        HHMMSSD     (7 digits)  — hours, minutes, seconds, tenths
        HHMMSSDD    (8 digits)  — hours, minutes, seconds, hundredths

    Decimal seconds are stored as microseconds:
        D  (tenths)     → multiplied by 100,000 microseconds
        DD (hundredths) → multiplied by  10,000 microseconds

    Parameters
    ----------
    time_str : str
        Time string of length 4, 6, 7, or 8 — digits only.

    Returns
    -------
    datetime
        datetime object with date components set to 1900-01-01 (default).
        Use parse_date_time() to combine with a date.

    Raises
    ------
    ValueError
        If the string length is not 4, 6, 7, or 8, contains non-digits,
        or the time value is not valid.

    Examples
    --------
    >>> parse_time('1200')
    datetime.datetime(1900, 1, 1, 12, 0)

    >>> parse_time('120000')
    datetime.datetime(1900, 1, 1, 12, 0, 0)

    >>> parse_time('1200005')
    datetime.datetime(1900, 1, 1, 12, 0, 0, 500000)

    >>> parse_time('12000055')
    datetime.datetime(1900, 1, 1, 12, 0, 0, 550000)
    '''
    time_str = time_str.strip()

    if not time_str.isdigit():
        raise ValueError(
            f"Invalid time string: '{time_str}'. Expected digits only."
        )

    length = len(time_str)

    if length in (7, 8):
        base = time_str[:6]
        # %f expects exactly 6 digits — pad right with zeros so tenths/hundredths
        # map correctly to microseconds (e.g. '5' → '500000', '55' → '550000')
        frac = time_str[6:].ljust(6, '0')
        return datetime.strptime(base + frac, '%H%M%S%f')

    formats = {
        4: '%H%M',
        6: '%H%M%S',
    }
    fmt = formats.get(length)
    if not fmt:
        raise ValueError(
            f"Unrecognized time format: '{time_str}'. "
            f"Expected HHMM (4), HHMMSS (6), HHMMSSD (7), or HHMMSSDD (8) digits, "
            f"got {length} digits."
        )
    return datetime.strptime(time_str, fmt)


def parse_date_time(date_str: str, time_str: str) -> datetime:
    '''
    Parse date and time strings and combine into a single datetime object.

    See parse_date() and parse_time() for all supported formats.

    Parameters
    ----------
    date_str : str
        Date string. See parse_date() for supported formats.
    time_str : str
        Time string. See parse_time() for supported formats.

    Returns
    -------
    datetime
        Fully combined datetime object with both date and time components.

    Examples
    --------
    >>> parse_date_time('20060101', '1200')
    datetime.datetime(2006, 1, 1, 12, 0)

    >>> parse_date_time('2006-01-01', '120000')
    datetime.datetime(2006, 1, 1, 12, 0, 0)

    >>> parse_date_time('01/01/2006', '12000055').isoformat()
    '2006-01-01T12:00:00.550000'
    '''
    d = parse_date(date_str)
    t = parse_time(time_str)
    return d.replace(hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond)
