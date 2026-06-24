import pandas as pd

correction_log: list[dict] = []

def correct_data_log(
        table_name: str,
        row_key,
        column_name: str,
        original_value,
        corrected_value,
        reason: str,
        source: str
) -> None:
    """
    Records a manual correction made during cleaning.
    Called every time a value is overwritten.
    """
    correction_log.append({
        "table_name": table_name,
        "row_key": row_key,
        "column_name": column_name,
        "original_value": original_value,
        "corrected_value": corrected_value,
        "reason": reason,
        "source": source
    })

def build_correction_table() -> pd.DataFrame:
    return pd.DataFrame(correction_log, columns=[
        "table_name", "row_key", "column_name", "original_value", "reason", "source"
    ])