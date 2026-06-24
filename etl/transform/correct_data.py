import pandas as pd
from transform.correct_data_log import *

def crops_seed_sell(df):
    """
    Corrects the crops seed sell price if the price is blank.
    Corrected data is also logged into the correct data logger.
    Args:
        df: The raw crops data.
    Returns:
        The data containing corrected values of seeds' sell prices, which is 1/2 of the buy price (floor).
    """
    mask = df["seed_sell"].isna() | (df["seed_sell"].astype(str).str.strip() == "")

    for i in df.loc[mask].index:
        correct_data_log(
            table_name="crops",
            row_key=df.at[i, "seed_name"],
            column_name="seed_sell",
            original_value=df.at[i, "seed_sell"],
            corrected_value=df.at[i, "seed_purchase"] / 2,
            reason="Blank seed_sell derived as half of seed_purchase",
            source="calculated",
        )

    df.loc[mask, "seed_sell"] = df.loc[mask, "seed_purchase"] / 2
    return df
def correct_crops_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Correct the crops data.
    Args:
        df: The raw crops data.
    Returns:
        df: The corrected crops data.
    """
    df_corrected = df.copy()
    df_corrected = crops_seed_sell(df_corrected)
    return df_corrected

def correct_data_manual(df, data, key, columns, table_name):
    df_corrected = df.copy()
    df_corrected = df_corrected.merge(data, on=key, how="left", suffixes=("", "_fill"))

    for column in columns:
        mask=df_corrected.isna() | (df_corrected[column].astype(str).str.strip() == "")

    return df_corrected