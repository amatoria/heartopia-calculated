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

    df_corrected = df.copy()
    mask = df_corrected["seed_sell"].isna() | (df["seed_sell"].astype(str).str.strip() == "")
    purchase_available = df["seed_purchase"].notna() & (df["seed_purchase"].astype(str).str.strip() != "")

    actionable_mask = mask & purchase_available
    skipped_mask = mask & ~purchase_available

    if skipped_mask.any():
        print(f"Warning: {skipped_mask.sum()} rows have blank seed_sell but also blank seed_purchase — skipped:")
        print(df.loc[skipped_mask, "seed_name"].tolist())

    for i in df_corrected.loc[actionable_mask].index:
        correct_data_log(
            table_name="crops",
            row_key=df_corrected.at[i, "seed_name"],
            column_name="seed_sell",
            original_value=df_corrected.at[i, "seed_sell"],
            corrected_value=int(df_corrected.at[i, "seed_purchase"] / 2),
            reason="Blank seed_sell derived as half of seed_purchase",
            source="calculated",
        )

    df_corrected.loc[actionable_mask, "seed_sell"] = (df.loc[actionable_mask, "seed_purchase"] / 2).astype(int)
    return df_corrected
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

def correct_data_manual(df, data, key, columns, table_name, source):
    df_corrected = df.copy()
    df_corrected = df_corrected.merge(data, on=key, how="left", suffixes=("", "_fill"))

    for column in columns:
        mask=df_corrected.isna() | (df_corrected[column].astype(str).str.strip() == "")

        for i in df_corrected.loc[mask].index:
            correct_data_log(
                table_name=table_name,
                row_key=df.at[i, key],
                column_name=column,
                original_value=df.at[i, column],
                corrected_value=df.at[i, f"{column}_fill"],
                reason="Missing from raw data. Filled from external source",
                source=source,
            )

        df_corrected.loc[mask,column] = df_corrected.loc[mask, f"{column}_fill"]
        df_corrected.drop(columns=[f"{column}_fill"], inplace=True)

    return df_corrected