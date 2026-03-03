from datetime import datetime

def list_edi_files_by_date(
    *,
    edi_type:   str,          # e.g. '214A'
    date_start: str,          # e.g. '2026-01-01'
    date_end:   str,          # e.g. '2026-01-20'
    location:   str = EDI_CONTAINER_LOCATION,
) -> pd.DataFrame:
    """
    List S3 files for a given EDI type filtered by filename date range.
    """
    edi_folder = f"dteb_{edi_type.lower()}/"
    files_df   = list_edi_files(edi_folder=edi_folder, location=location)

    # Parse date from filename  e.g. dteb_315a_20260101_...
    files_df['FileDate'] = pd.to_datetime(
        files_df['Name'].str.extract(rf'{edi_type}_(\d{{8}})', expand=False),
        format='%Y%m%d',
        errors='coerce'
    )

    start = pd.Timestamp(date_start)
    end   = pd.Timestamp(date_end)

    return files_df[files_df['FileDate'].between(start, end)].reset_index(drop=True)


# ------------- Usage
df = list_edi_files_by_date(
    edi_type   = '214A',
    date_start = '2026-01-01',
    date_end   = '2026-01-20',
)
display(df)
