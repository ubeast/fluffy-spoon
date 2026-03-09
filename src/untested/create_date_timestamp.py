from datetime import datetime, date

def create_date_timestamp(
    date_val: str,
    time_val: str,
    date_fmt_input: str,
    time_fmt_input: str,
    *,
    date_only: bool = False,
) -> datetime:
    """
    Parse date and time strings into a datetime object.

    Args:
        date_val:       Date string e.g. '20260112' or '260112'.
        time_val:       Time string e.g. '2345'.
        date_fmt_input: Date format using CCYY/YY/MM/DD e.g. 'CCYYMMDD'.
        time_fmt_input: Time format using HH/MM/SS e.g. 'HHMM'.
        date_only:      If True, return date only. Default returns datetime with zeroed seconds.

    Returns:
        datetime.date if date_only=True, otherwise datetime with seconds zeroed.

    Examples:
        >>> from datetime import datetime, date
        >>> create_date_timestamp('20260112', '2345', 'CCYYMMDD', 'HHMM')
        datetime.datetime(2026, 1, 12, 23, 45)

        >>> create_date_timestamp('260112', '2345', 'CCYYMMDD', 'HHMM')
        datetime.datetime(2026, 1, 12, 23, 45)

        >>> create_date_timestamp('20260112', '2345', 'CCYYMMDD', 'HHMM', date_only=True)
        datetime.date(2026, 1, 12)
    """
    if len(date_val) == 6:
        date_fmt_input = date_fmt_input.replace('CCYY', 'YY')

    translated_date_fmt = (date_fmt_input.replace('CCYY', '%Y')
                                         .replace('YY', '%y')
                                         .replace('MM', '%m')
                                         .replace('DD', '%d'))
    translated_time_fmt = (time_fmt_input.replace('HH', '%H')
                                         .replace('MM', '%M')
                                         .replace('SS', '%S'))

    dt_obj = datetime.strptime(f"{date_val} {time_val}", f"{translated_date_fmt} {translated_time_fmt}")

    if date_only:
        return dt_obj.date()
    return dt_obj.replace(second=0, microsecond=0)

#import doctest
#doctest.testmod()
