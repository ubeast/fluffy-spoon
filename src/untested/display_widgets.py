"""
Template for creating standard reporting widgets in a Databricks notebook.

Provides a reusable framework for generating dropdown widgets used to filter
reports. Requires the `dbutils` object from the Databricks environment.

Programmatic values:
    MONTH_NBRS:   Month numbers '1' to '12'.
    YEARS_MINUS_3: Current year plus the three preceding years e.g. ['2026', '2025', '2024', '2023'].

Usage:
    from cfuncs.display_widgets import display_widgets
    display_widgets(dbutils)

    Access selected values in subsequent cells:
    dbutils.widgets.get("WidgetName")
"""
from datetime import datetime, timezone
import logging

# --- Date Values ---
DATETIMESTAMP_UTC:   datetime = datetime.now(timezone.utc)
DATETIMESTAMP_LOCAL: datetime = DATETIMESTAMP_UTC.astimezone()

# --- Widget Choices ---
COCOMS:       list      = ['AFRICOM', 'EUCOM', 'CENTCOM', 'NORTHCOM', 'SOUTHCOM', 'INDOPACOM']
REPORT_TYPES: list      = ['Monthly', 'Quarterly']
MONTH_NBRS:   list[str] = [str(i) for i in range(1, 13)]
YEARS_MINUS_3: list[str] = [str(DATETIMESTAMP_LOCAL.year - i) for i in range(4)]


def display_widgets(_dbutils) -> None:
    """
    Create standard reporting dropdown widgets in a Databricks notebook.

    Args:
        _dbutils: Databricks dbutils object.

    Examples:
        >>> from unittest.mock import MagicMock
        >>> dbutils = MagicMock()
        >>> display_widgets(dbutils)
        >>> dbutils.widgets.dropdown.call_count
        4
    """
    widgets = [
        {'name': 'COCOM',        'defaultValue': 'AFRICOM',                     'choices': COCOMS,        'label': "Identify your COCOM"},
        {'name': 'Report Type',  'defaultValue': 'Quarterly',                   'choices': REPORT_TYPES,  'label': "Monthly or Quarterly"},
        {'name': 'Report Year',  'defaultValue': str(DATETIMESTAMP_LOCAL.year), 'choices': YEARS_MINUS_3, 'label': "Report Year"},
        {'name': 'Report Month', 'defaultValue': str(DATETIMESTAMP_LOCAL.month),'choices': MONTH_NBRS,    'label': "Report Month"},
    ]

    for w in widgets:
        try:
            _dbutils.widgets.dropdown(**w)
        except Exception as e:
            logging.warning(f"Failed to create widget '{w['name']}': {e}")




