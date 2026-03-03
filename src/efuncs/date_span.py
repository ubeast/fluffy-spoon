from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass


@dataclass(frozen=True)
class DateSpan:
    start: date
    end:   date

    def __len__(self) -> int:
        """Number of days in the span, inclusive of both endpoints."""
        return (self.end - self.start).days + 1

    def __contains__(self, item: date) -> bool:
        """Allows: date(2026, 1, 15) in span"""
        return self.start <= item <= self.end

    def __iter__(self):
        """Allows tuple unpacking: start, end = span"""
        yield self.start
        yield self.end

    @property
    def days(self) -> int:
        """Number of days in the span, inclusive of both endpoints."""
        return len(self)

    @property
    def months(self) -> int:
        """Approximate number of months in the span, inclusive of both endpoints."""
        delta = relativedelta(self.end, self.start)
        return delta.months + (delta.years * 12) + 1


def date_span(*, anchor_date: date | str, month_offset: int) -> DateSpan:
    """
    Calculates a date span, returning the first day and last day of a period.

    The function anchors itself to the provided date and calculates a new date by
    adding or subtracting a number of months. It then returns the first day of the
    earlier month and the last day of the later month as a DateSpan object.

    Args:
        anchor_date:  The date to calculate from. Can be a date object or a
                      string in 'YYYY-MM-DD' format.
        month_offset: The number of months to offset from the anchor date.
                      A negative integer (-12) goes back in time.
                      A positive integer (3) goes forward in time.
                      Zero (0) returns the start and end of the anchor month.

    Returns:
        A DateSpan object with .start and .end date attributes.

    Raises:
        TypeError:  If anchor_date is not a date object or 'YYYY-MM-DD' string.
        ValueError: If anchor_date is a string that cannot be parsed as a date.

    Examples:
        >>> span = date_span(anchor_date='2026-01-10', month_offset=-12)
        >>> print(f"Going back 12 months: {span.start} to {span.end}")
        Going back 12 months: 2025-01-01 to 2026-01-31

        >>> span = date_span(anchor_date='2026-01-10', month_offset=3)
        >>> print(f"Going forward 3 months: {span.start} to {span.end}")
        Going forward 3 months: 2026-01-01 to 2026-04-30

        >>> span = date_span(anchor_date='2026-01-10', month_offset=0)
        >>> print(f"Same month: {span.start} to {span.end}")
        Same month: 2026-01-01 to 2026-01-31

        >>> # Tuple unpacking still works
        >>> start, end = date_span(anchor_date='2026-01-10', month_offset=-12)

        >>> # Membership test
        >>> date(2026, 1, 15) in date_span(anchor_date='2026-01-10', month_offset=0)
        True

        >>> # Length in days
        >>> len(date_span(anchor_date='2026-01-10', month_offset=0))
        31
    """
    # Validate and convert the input date
    if isinstance(anchor_date, str):
        anchor_date = date.fromisoformat(anchor_date)  # Raises ValueError if invalid
    elif not isinstance(anchor_date, date):
        raise TypeError("anchor_date must be a date object or a string in 'YYYY-MM-DD' format.")

    # Calculate the target date based on the offset
    target_date = anchor_date + relativedelta(months=month_offset)

    # Determine which date is earlier and which is later
    start_ref = min(anchor_date, target_date)
    end_ref   = max(anchor_date, target_date)

    # First day of the start month
    period_start = start_ref.replace(day=1)

    # Last day of the end month
    period_end = end_ref.replace(day=1) + relativedelta(months=1) - timedelta(days=1)

    return DateSpan(start=period_start, end=period_end)
