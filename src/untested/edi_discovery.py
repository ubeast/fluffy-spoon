# edi_discovery.py
# edi_catalog.py
# edi_inventory.py


import pandas as pd

# --- Constants
EDI_CONTAINER_LOCATION = 's3://advana-data-zone/bronze/dla_daas/edi/'

EXCLUDE_NAMES = {'', 'name}', 'tmp', 'failed', 'completed', 'archive',
                 'staging', 'backlog', 'tracking', 'december2025'}

RENAME_NAMES = {'856rtemp': '856r (temp)'}


# --- Functions

def get_dir_list(*, location: str) -> pd.DataFrame:
    """
    List directory contents as a DataFrame.

    Args:
        location: S3 path to list.

    Returns:
        DataFrame with columns: Path, Name, ByteSize, ModificationTime.

    Examples:
        | Path                                                 | Name       | ByteSize | ModificationTime              |
        | s3://advana-data-zone/bronze/dla_daas/edi/dteb_214a/ | dteb_214a/ |     0    | 2026-02-27T16:19:27.714+00:00 |
        | s3://advana-data-zone/bronze/dla_daas/edi/dteb_315a/ | dteb_315a/ |     0    | 2026-02-27T16:19:27.714+00:00 |
    """
    dir_list = dbutils.fs.ls(location)
    df = pd.DataFrame(dir_list, columns=['Path', 'Name', 'ByteSize', 'ModificationTime'])
    df['ModificationTime'] = pd.to_datetime(df['ModificationTime'], unit='ms')
    return df.sort_values('Path')


def _parse_edi_name(name: str) -> str:
    """Extract and clean EDI type from a folder name e.g. 'dteb_214a/' -> '214A'."""
    cleaned = (name.strip('/')
                   .split('_')[-1]
                   .lower())
    cleaned = RENAME_NAMES.get(cleaned, cleaned)
    return '' if cleaned in EXCLUDE_NAMES else cleaned.upper()


def get_list_of_available_edis(*, location: str) -> list:
    """
    Return sorted list of unique EDI types found at location.

    Args:
        location: S3 path to scan.

    Returns:
        Sorted list of EDI type strings e.g. ['180M', '214A', '315A'].
    """
    df = get_dir_list(location=location)
    edis = {_parse_edi_name(name) for name in df.Name}
    return sorted(edis - {''})


def get_table_of_available_flatfiles(*, edi_folder: str, location: str) -> pd.DataFrame:
    """
    List flat files available for a given EDI folder.

    Args:
        edi_folder: EDI subfolder name e.g. 'dteb_214a'.
        location:   Base S3 path.

    Returns:
        DataFrame of files in the EDI folder.
    """
    if not edi_folder.endswith('/'):
        edi_folder += '/'
    return get_dir_list(location=location + edi_folder)


def _parse_owner(name: str) -> str:
    if 'dedso' in name: return 'DLA'
    if 'dteb'  in name: return 'DTEB'
    return ''


def _parse_edi_nbr(name: str) -> str:
    segment = name.split('dteb_')[-1].split('dedso_')[-1].split('_')[0].replace('temp', '')[:-1]
    return segment[:3] if segment[:3].isdigit() else ''


def _parse_edi_alpha(name: str) -> str:
    segment = name.split('dteb_')[-1].split('dedso_')[-1].split('_')[0].replace('temp', '')[:-1]
    return segment[-1].upper() if segment[:3].isdigit() else ''


# --- Prepopulate

list_of_available_edis_in_daas = get_list_of_available_edis(location=EDI_CONTAINER_LOCATION)
df_of_available_edis_in_daas   = get_dir_list(location=EDI_CONTAINER_LOCATION)

df_of_available_edis_in_daas['Owner']     = df_of_available_edis_in_daas.Name.apply(_parse_owner)
df_of_available_edis_in_daas['edi_nbr']   = df_of_available_edis_in_daas.Name.apply(_parse_edi_nbr)
df_of_available_edis_in_daas['edi_alpha'] = df_of_available_edis_in_daas.Name.apply(_parse_edi_alpha)

# --- Display
print(f'\nAVAILABLE EDIs: {list_of_available_edis_in_daas}\n')
print('TABLE OF FOLDERS CONTAINING EDIs:')
display(df_of_available_edis_in_daas)
