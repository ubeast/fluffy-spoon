def sql_get_edi_files(
    *,
    edi_type:   str,          # e.g. '315A'
    date_start: str,          # e.g. '2026-01-01'
    date_end:   str,          # e.g. '2026-01-20'
    schema:     str = 'dla_daas',
) -> pd.DataFrame:
    """
    Query a DAAS EDI table filtering by EDI type and observation date range.
    """
    table = f"dteb_{edi_type.lower()}"

    query = f"""
        SELECT
            element_at(split(regexp_replace(advanasys_filename_raw, '\\.complete$', ''), '/'), -1)
                                                            AS FIL_NM,
            TO_DATE(
                SUBSTRING(
                    advanasys_filename_raw,
                    CHARINDEX('{edi_type}_', advanasys_filename_raw) + 5,
                    8
                ), 'yyyyMMdd'
            )                                               AS OBSRVN_DT,
            advanasys_filename_raw                          AS RAW_PATH
        FROM {schema}.{table}
        WHERE TO_DATE(
                SUBSTRING(
                    advanasys_filename_raw,
                    CHARINDEX('{edi_type}_', advanasys_filename_raw) + 5,
                    8
                ), 'yyyyMMdd'
              ) BETWEEN '{date_start}' AND '{date_end}'
    """

    return spark.sql(query).distinct().toPandas()


# ------------- Usage
df = sql_get_edi_files(
    edi_type   = '315A',
    date_start = '2026-01-01',
    date_end   = '2026-01-20',
)
display(df)
