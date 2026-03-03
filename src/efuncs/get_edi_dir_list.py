import pandas as pd

# ------------- Constants
EDI_CONTAINER_LOCATION = 's3://advana-data-zone/bronze/dla_daas/edi/'

# Names to exclude when building the list of available EDIs
EXCLUDED_FOLDER_SUFFIXES = {
    'name}', 'tmp', 'failed', 'completed', 'archive',
    'staging', 'backlog', 'tracking', 'december2025', ''
}

SPECIAL_CASE_RENAMES = {
    '856rtemp': '856R (TEMP)',
}


# ------------- Get directory contents as dataframe
def get_dir_list(*, location: str) -> pd.DataFrame:
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


# ------------- Helper: parse EDI code from a folder name
def _parse_edi_code(folder_name: str) -> str:
    """
    Extract the EDI identifier from a folder name like 'dteb_214a/' or 'dedso_856r/'.
    Returns the EDI code (e.g. '214A') or an empty string if not parseable.
    """
    # Strip trailing slash, split on underscore, take the last token
    token = folder_name.rstrip('/').split('_')[-1].replace('temp', '').upper()
    return SPECIAL_CASE_RENAMES.get(token.lower(), token)


# ------------- Get available EDI types as a sorted list
def get_list_of_available_edis(*, location: str) -> list:
    '''
    Return Sample:
        ['180M', '214A', '315A', '315B', '315N', '511M', '511R', '527R', '856A']
    '''
    dir_list_df = get_dir_list(location=location)
    edi_codes = set(dir_list_df['Name'].apply(_parse_edi_code))
    edi_codes -= EXCLUDED_FOLDER_SUFFIXES
    return sorted(edi_codes)


# ------------- Get available EDI flat files as dataframe
def get_table_of_available_flatfiles(*, edi_folder: str, location: str) -> pd.DataFrame:
    edi_folder = edi_folder.rstrip('/') + '/'
    return get_dir_list(location=location + edi_folder)


# ------------- Helper: parse owner, EDI number, and EDI alpha from a folder name
def _parse_owner(name: str) -> str:
    if 'dedso' in name:
        return 'DLA'
    if 'dteb' in name:
        return 'DTEB'
    return ''


def _parse_edi_nbr_alpha(name: str) -> tuple[str, str]:
    """Returns (edi_nbr, edi_alpha) from a folder name, or ('', '') if not parseable."""
    token = name.split('dteb_')[-1].split('dedso_')[-1].split('_')[0].replace('temp', '').rstrip('/')
    # Expect format like '214a' — first 3 chars are digits, last char is alpha
    if len(token) >= 4 and token[:3].isdigit():
        return token[:3], token[3].upper()
    return '', ''


# ------------- Prepopulate variables
list_of_available_edis_in_daas: list = get_list_of_available_edis(location=EDI_CONTAINER_LOCATION)
df_of_available_edis_in_daas: pd.DataFrame = get_dir_list(location=EDI_CONTAINER_LOCATION)

# ------------- Parse owner, EDI number, and EDI alpha
df_of_available_edis_in_daas['Owner'] = df_of_available_edis_in_daas['Name'].apply(_parse_owner)

nbr_alpha = df_of_available_edis_in_daas['Name'].apply(_parse_edi_nbr_alpha)
df_of_available_edis_in_daas['edi_nbr']   = nbr_alpha.apply(lambda x: x[0])
df_of_available_edis_in_daas['edi_alpha'] = nbr_alpha.apply(lambda x: x[1])

# ------------- Display
print(f'\nAVAILABLE EDIs: {list_of_available_edis_in_daas}\n')
print('TABLE OF FOLDERS CONTAINING EDIs:')
display(df_of_available_edis_in_daas)
