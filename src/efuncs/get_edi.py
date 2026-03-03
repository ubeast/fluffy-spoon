# ------------- Constants
SCHEMA   = 'dla_daas'
TABLE    = 'dteb_315a'
EDI_TYPE = '315A'


def sql_get_raw_edi_files(
    *,
    edi_type:      str = EDI_TYPE,
    schema:        str = SCHEMA,
    table:         str = TABLE,
    filename_like: str | None = None,
) -> str:
    """
    Build a SQL query to extract raw EDI file records from a Databricks table.

    Args:
        edi_type:      EDI type code used to locate the date substring (e.g. '315A').
        schema:        Database schema name.
        table:         Table name within the schema.
        filename_like: Optional LIKE filter on advanasys_filename_raw
                       (e.g. '%20240205_190509000_0000001140%').
                       If None, no filter is applied.

    Returns:
        A SQL string ready to pass to spark.sql().

    Example output columns:
        FIL_NM          - Filename stripped of path and .complete extension
        TRNSCN_SET_CTL_ID - Raw transaction set control number
        r4_values       - Raw R4 segment values
        SRC_NM          - Hardcoded source name ('DAAS')
        FIL_REC_NB      - Transaction set control number cast to INT
        OBSRVN_DT       - Observation date parsed from filename
    """
    where_clause = f"WHERE advanasys_filename_raw LIKE '{filename_like}'" if filename_like else ''

    return f"""
        SELECT
            element_at(split(regexp_replace(advanasys_filename_raw, '\\.complete$', ''), '/'), -1)
                                                            AS FIL_NM,
            transaction_set_control_number_st               AS TRNSCN_SET_CTL_ID,
            r4_values,
            'DAAS'                                          AS SRC_NM,
            CAST(transaction_set_control_number_st AS INT)  AS FIL_REC_NB,
            TO_DATE(
                SUBSTRING(
                    advanasys_filename_raw,
                    CHARINDEX('{edi_type}_', advanasys_filename_raw) + 5,
                    8
                ), 'yyyyMMdd'
            )                                               AS OBSRVN_DT
        FROM {schema}.{table}
        {where_clause}
    """


# ------------- Execute
df = spark.sql(
    sql_get_raw_edi_files(
        filename_like='%20240205_190509000_0000001140%'
    )
)
df.display()
