import pandas as pd

def pandas_show_as_markdown(df: pd.DataFrame) -> str:
    """
    Convert a Pandas DataFrame to a Markdown table, print it, and copy to clipboard.
    Clipboard copy is skipped silently if pyperclip is not installed.

    Args:
        df: DataFrame to convert.

    Returns:
        Markdown formatted string of the table.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> result = convert_pandas_table_to_markdown(df)
        |   A |   B |
        |----:|----:|
        |   1 |   3 |
        |   2 |   4 |
    """
    md = df.to_markdown(index=False)
    print(md)

    try:
        import pyperclip
        pyperclip.copy(md)
    except ImportError:
        pass

    return md

# Attach to DataFrame
pd.DataFrame.show_as_markdown = show_as_markdown
pd.DataFrame.to_csv_from_excel = to_csv_from_excel

#import my_package.utils.pandas_utils

#import doctest
#doctest.testmod()
