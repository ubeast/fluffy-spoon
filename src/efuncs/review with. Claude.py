def display_dynamic_widgets(_dbutils, edi_list: list):
    """
    Creates standard widgets plus a dynamic EDI Type selector.
    
    Args:
        _dbutils: The Databricks dbutils object.
        edi_list: The list of available EDI types (e.g., ['214A', '856A']).
    """
    # Ensure we have a default if the list is empty
    default_edi = edi_list[0] if edi_list else "NONE"
    
    widgets_to_create = [
        {'name': 'EDI Type', 
         'defaultValue': default_edi, 
         'choices': edi_list if edi_list else ["NONE"], 
         'label': "Select EDI Transaction"},

        {'name': 'COCOM', 
         'defaultValue': 'AFRICOM', 
         'choices': COCOMS, 
         'label': "Identify your COCOM"},
        
        {'name': 'Report Type', 
         'defaultValue': 'Quarterly', 
         'choices': REPORT_TYPES, 
         'label': "Monthly or Quarterly"},
        
        {'name': 'Report Year', 
         'defaultValue': str(DATETIMESTAMP_LOCAL.year), 
         'choices': YEARS_MINUS_3, 
         'label': "Report Year"},
        
        {'name': 'Report Month', 
         'defaultValue': str(DATETIMESTAMP_LOCAL.month), 
         'choices': MONTH_NBRS, 
         'label': "Report Month"}
    ]

    for widget_params in widgets_to_create:
        try:
            _dbutils.widgets.dropdown(**widget_params)
        except Exception as e:
            logging.warning(f"Failed to create widget '{widget_params['name']}': {e}")

# --- Implementation in your Notebook ---
# 1. Get the list from your previous S3 logic
# available_edis = get_list_of_available_edis(location=EDI_CONTAINER_LOCATION)

# 2. Display the widgets
# display_dynamic_widgets(dbutils, available_edis)
