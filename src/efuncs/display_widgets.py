"""Template for creating standard widgets in a Databricks notebook.

This module provides a reusable framework for generating a set of dropdown
widgets commonly used for filtering reports. It is designed to be easily
customizable and depends on the `dbutils` object provided by the Databricks
environment.

Key Programmatic Features:
  - MONTH_NBRS:    Programmatically generates a list of month numbers ('1' to '12').
  - YEARS_MINUS_3: Programmatically generates a list containing the current
                   year plus the three preceding years (e.g., ['2024', '2023', '2022', '2021']).

How to Use:
  1. In your Databricks notebook, import and call the function like this:
```python
     from cfuncs.display_widgets import display_widgets
     display_widgets(dbutils)
```
  2. Access the selected widget values in subsequent cells using:
     `dbutils.widgets.get("WidgetName")`.
"""
from datetime import datetime, timezone
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# ------------- Timestamps
DATETIMESTAMP_UTC:   datetime = datetime.now(timezone.utc)
DATETIMESTAMP_LOCAL: datetime = DATETIMESTAMP_UTC.astimezone()

# ------------- Widget choices
COCOMS:       list[str] = ['AFRICOM', 'EUCOM', 'CENTCOM', 'NORTHCOM', 'SOUTHCOM', 'INDOPACOM']
REPORT_TYPES: list[str] = ['Monthly', 'Quarterly']
MONTH_NBRS:   list[str] = [str(i) for i in range(1, 13)]
YEARS_MINUS_3: list[str] = [str(DATETIMESTAMP_LOCAL.year - i) for i in range(4)]


@dataclass
class WidgetDef:
    """Definition for a single Databricks dropdown widget."""
    name:         str
    defaultValue: str
    choices:      list[str]
    label:        str


WIDGET_DEFINITIONS: list[WidgetDef] = [
    WidgetDef(
        name         = 'COCOM',
        defaultValue = 'AFRICOM',
        choices      = COCOMS,
        label        = 'Identify your COCOM',
    ),
    WidgetDef(
        name         = 'Report Type',
        defaultValue = 'Quarterly',
        choices      = REPORT_TYPES,
        label        = 'Monthly or Quarterly',
    ),
    WidgetDef(
        name         = 'Report Year',
        defaultValue = str(DATETIMESTAMP_LOCAL.year),
        choices      = YEARS_MINUS_3,
        label        = 'Report Year',
    ),
    WidgetDef(
        name         = 'Report Month',
        defaultValue = str(DATETIMESTAMP_LOCAL.month),
        choices      = MONTH_NBRS,
        label        = 'Report Month',
    ),
]


def display_widgets(_dbutils) -> None:
    """
    Create all standard report dropdown widgets in a Databricks notebook.

    Args:
        _dbutils: The Databricks dbutils object, passed in from the notebook.

    Raises:
        Logs a warning for each widget that fails to create rather than
        raising an exception, so remaining widgets are always attempted.
    """
    for widget in WIDGET_DEFINITIONS:
        try:
            _dbutils.widgets.dropdown(
                name         = widget.name,
                defaultValue = widget.defaultValue,
                choices      = widget.choices,
                label        = widget.label,
            )
        except Exception as e:
            logger.warning(f"Failed to create widget '{widget.name}': {e}")
