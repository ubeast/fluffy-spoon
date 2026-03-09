def get_widget_values(_dbutils) -> dict:
    """
    Retrieve current values of the standard reporting widgets.

    Args:
        _dbutils: Databricks dbutils object.

    Returns:
        Dictionary of selected filter values, or empty dict on failure.

    Examples:
        >>> from unittest.mock import MagicMock
        >>> dbutils = MagicMock()
        >>> dbutils.widgets.get.side_effect = lambda k: {'COCOM': 'USEUCOM', 'Report Type': 'Monthly', 'Report Year': '2026', 'Report Month': '01'}[k]
        >>> get_widget_values(dbutils)
        {'cocom': 'USEUCOM', 'report_type': 'Monthly', 'report_year': '2026', 'report_month': '01'}
    """
    try:
        return {
            'cocom':        _dbutils.widgets.get("COCOM"),
            'report_type':  _dbutils.widgets.get("Report Type"),
            'report_year':  _dbutils.widgets.get("Report Year"),
            'report_month': _dbutils.widgets.get("Report Month"),
        }
    except Exception as e:
        logging.error(f"Error retrieving widget values: {e}")
        return {}

#import doctest
#doctest.testmod(verbose=True)
