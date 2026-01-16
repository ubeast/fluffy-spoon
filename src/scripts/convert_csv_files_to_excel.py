from glob import glob
import pandas as pd

def convert_csv_files_to_excel(files: list):
    [pd.read_csv(_).to_excel(_.replace('.csv', '.xlsx'), index = False) for _ in files]
