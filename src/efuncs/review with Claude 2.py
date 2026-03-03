def get_widget_values(_dbutils) -> dict:
    """
    Retrieves the current values of the standard reporting widgets.
    
    Returns:
        dict: A dictionary containing the selected filter values.
    """
    try:
        filters = {
            'cocom': _dbutils.widgets.get("COCOM"),
            'report_type': _dbutils.widgets.get("Report Type"),
            'report_year': _dbutils.widgets.get("Report Year"),
            'report_month': _dbutils.widgets.get("Report Month")
        }
        return filters
    except Exception as e:
        logging.error(f"Error retrieving widget values: {e}")
        return {}

# Example Usage in a Databricks cell:
# selected_filters = get_widget_values(dbutils)
# print(f"Processing data for {selected_filters['cocom']} - {selected_filters['report_year']}")
