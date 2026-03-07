from datetime import datetime

def create_date_timestamp(date_val, time_val, date_fmt_input, time_fmt_input, 
                          include_date=True, include_hour=True, include_seconds=False):
    
    # 1. Convert your formats (CCYYMMDD) into the codes Python understands (%Y%m%d)
    # We'll call these 'translated' formats
    translated_date_fmt = date_fmt_input.replace('CCYY', '%Y').replace('YY', '%y').replace('MM', '%m').replace('DD', '%d')
    translated_time_fmt = time_fmt_input.replace('HH', '%H').replace('MM', '%M').replace('SS', '%S')
    
    # 2. Combine them into the single "Master" format and string
    dt_format = f"{translated_date_fmt} {translated_time_fmt}"
    dt_string = f"{date_val} {time_val}"
    
    # 3. Create the timestamp object
    dt_obj = datetime.strptime(dt_string, dt_format)

    # 4. Map the flags to the output string you want
    return_map = {
        (True, True, True):  "%Y-%m-%d %H:%M:%S",
        (True, True, False): "%Y-%m-%d %H:%M",
        (True, False, False): "%Y-%m-%d",
    }

    output_format = return_map.get((include_date, include_hour, include_seconds), "%Y-%m-%d")
    
    return dt_obj.strftime(output_format)
