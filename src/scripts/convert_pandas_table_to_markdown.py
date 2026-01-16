import pandas as pd
import pyperclip

def convert_pandas_table_to_markdown(df):
    md = df.to_markdown(index=False)
    pyperclip.copy(md)
#    print('Your markdown of the table below has been saved to your clipboard.')
#    print('The text below is for you to be able to see what is in your clipboard.')
#    print()
    #print(md)

    return md
