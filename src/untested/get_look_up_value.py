import json
import os

def get_look_up_value(segment_element: str, 
                     data_element: str, 
                     lookup_key: str, 
                     include_lookup_code=True):

    # 1. Determine the filename based on the data element
    ref_table_name = f"{data_element}.json"
    
    # 2. Read the JSON file
    # (Assuming the JSON is a simple key-value pair dictionary)
    try:
        with open(ref_table_name, 'r') as f:
            ref_table = json.load(f)
    except FileNotFoundError:
        return f"Error: {ref_table_name} not found"

    # 3. Perform the lookup
    # .get() prevents crashing if the key is missing
    lookup_value = ref_table.get(str(lookup_key), "Unknown Value")

    # 4. Format the output based on your logic
    # Logic: Value + (Key) or Value + (Key)(DTEB)
    if include_lookup_code:
        return f"{lookup_value} ({lookup_key})(DTEB)"
    else:
        return f"{lookup_value} ({lookup_key})"

# Example Usage:
# If 145.json contains {"BN402": "Beneficiary Name"}
# result = get_look_up_value('BN402', '145', 'BN402')
# print(result) -> "Beneficiary Name (BN402)(DTEB)"
