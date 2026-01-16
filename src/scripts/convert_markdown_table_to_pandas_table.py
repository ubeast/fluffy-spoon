import pandas as pd
from io import StringIO

def convert_markdown_table_to_pandas_table(markdown_table: str) -> pd.DataFrame:

    # Remove Markdown borders and convert to CSV-like format
    
    data = "\n".join(
        line.strip().strip("|") for line in markdown_table.strip().splitlines()
        if line.strip() and not line.startswith("|-")
    )
    
    df = pd.read_csv(StringIO(data), sep="|")

    if ''.join(df.iloc[0].tolist()).replace('-', '').replace(':', '').strip():
        return df
    else:
        return df.iloc[1:]
