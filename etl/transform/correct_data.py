import pandas as pd

def crops_seed_sell(df):
    """
    Corrects the crops seed sell price if the price is blank.
    Args:
        df: The raw crops data.
    Returns:
        The data containing corrected values of seeds' sell prices, which is 1/2 of the buy price (floor).
    """
    df_corrected = df.copy()
    # Checking for empty seed_sell cells
    mask = df_corrected["seed_sell"].isna() | (df_corrected["seed_sell"].astype(str).str.strip() == "")
    df_corrected.loc[mask, "seed_sell"] = df_corrected.loc[mask, "seed_purchase"] / 2
    df_corrected.loc[mask, "notes"] = "Added seed_sell value as seed_purchase/2"
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