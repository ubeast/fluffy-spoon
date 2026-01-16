from glob import glob
import pandas as pd

def convert_excel_files_to_csv(files: list):
    [pd.read_excel(_).to_csv(_.replace('.xlsx', '.csv'), index = False) for _ in files]
