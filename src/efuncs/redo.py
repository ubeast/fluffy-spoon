```python
import pandas as pd

# ------------- Constants
EDI_CONTAINER_LOCATION = 's3://advana-data-zone/bronze/dla_daas/edi/'

EXCLUDED_FOLDER_SUFFIXES = {
    'name}', 'tmp', 'failed', 'completed', 'archive',
    'staging', 'backlog', 'tracking', 'december2025', ''
}

SPECIAL_CASE_RENAMES = {
    '856rtemp': '856R (TEMP)',
}


# ------------- Get directory contents as dataframe
def list_s3_folder(*, location: str) -> pd.DataFrame:
    '''
    Return Sample:
        |------------------------------------------------------|------------|----------|-------------------------------|
        | Path                                                 | Name       | ByteSize | ModificationTime              |
        |------------------------------------------------------|------------|----------|-------------------------------|
        | s3://advana-data-zone/bronze/dla_daas/edi/dteb_214a/ | dteb_214a/ |     0    | 2026-02-27T16:19:27.714+00:00 |
        | s3://advana-data-zone/bronze/dla_daas/edi/dteb_315a/ | dteb_315a/ |     0    | 2026-02-27T16:19:27.714+00:00 |
    '''
    dir_list: list = dbutils.fs.ls(location)
    dir_list_df = pd.DataFrame(dir_list, columns=['Path', 'Name', 'ByteSize', 'ModificationTime'])
    dir_list_df['ModificationTime'] = pd.to_datetime(dir_list_df['ModificationTime'], unit='ms')
    dir_list_df = dir_list_df.sort_values('Path').reset_index(drop=True)
    return dir_list_df


# ------------- Helper: convert folder name to EDI code
def _folder_name_to_edi_code(folder_name: str) -> str:
    """
    Extract the EDI identifier from a folder name like 'dteb_214a/' or 'dedso_856r/'.
    Returns the EDI code (e.g. '214A') or an empty string if not parseable.
    """
    token = folder_name.rstrip('/').split('_')[-1].replace('temp', '').upper()
    return SPECIAL_CASE_RENAMES.get(token.lower(), token)


# ------------- Get available EDI types as a sorted list
def list_edi_types(*, location: str) -> list:
    '''
    Return Sample:
        ['180M', '214A', '315A', '315B', '315N', '511M', '511R', '527R', '856A']
    '''
    edi_folders_df = list_s3_folder(location=location)
    edi_codes = set(edi_folders_df['Name'].apply(_folder_name_to_edi_code))
    edi_codes -= EXCLUDED_FOLDER_SUFFIXES
    return sorted(edi_codes)


# ------------- Get available EDI flat files as dataframe
def list_edi_files(*, edi_folder: str, location: str) -> pd.DataFrame:
    edi_folder = edi_folder.rstrip('/') + '/'
    return list_s3_folder(location=location + edi_folder)


# ------------- Helper: convert folder name to owner
def _folder_name_to_owner(name: str) -> str:
    if 'dedso' in name:
        return 'DLA'
    if 'dteb' in name:
        return 'DTEB'
    return ''


# ------------- Helper: convert folder name to (edi_nbr, edi_alpha)
def _folder_name_to_nbr_alpha(name: str) -> tuple[str, str]:
    """Returns (edi_nbr, edi_alpha) from a folder name, or ('', '') if not parseable."""
    token = name.split('dteb_')[-1].split('dedso_')[-1].split('_')[0].replace('temp', '').rstrip('/')
    # Expect format like '214a' — first 3 chars are digits, last char is alpha
    if len(token) >= 4 and token[:3].isdigit():
        return token[:3], token[3].upper()
    return '', ''


# ------------- Prepopulate variables
edi_types:      list         = list_edi_types(location=EDI_CONTAINER_LOCATION)
edi_folders_df: pd.DataFrame = list_s3_folder(location=EDI_CONTAINER_LOCATION)

# ------------- Parse owner, EDI number, and EDI alpha
edi_folders_df['Owner'] = edi_folders_df['Name'].apply(_folder_name_to_owner)

edi_nbr_alpha_series = edi_folders_df['Name'].apply(_folder_name_to_nbr_alpha)
edi_folders_df['edi_nbr']   = edi_nbr_alpha_series.apply(lambda x: x[0])
edi_folders_df['edi_alpha'] = edi_nbr_alpha_series.apply(lambda x: x[1])

# ------------- Display
print(f'\nAVAILABLE EDIs: {edi_types}\n')
print('TABLE OF FOLDERS CONTAINING EDIs:')
display(edi_folders_df)
```
