import gspread
import pandas as pd

gc = gspread.service_account()
sheet = gc.open("Copy of Heartopia Guide - updated April 21st")


def get_data(worksheet_number, cell_values):
    """
    Get the data from the worksheet.
    Args:
        worksheet_number: The number of the worksheet to get the data from.
        cell_values: The cells to get the data from.
    Returns:
        data: The data from the worksheet.
    """
    return sheet.get_worksheet(worksheet_number).get(cell_values)

def convert_to_df(data) -> pd.DataFrame:
    """
    Convert the data to a DataFrame.
    Args:
        data: The data to convert to a DataFrame.
    Returns:
        df: The DataFrame.
    """
    if not data:
        return pd.DataFrame()
    
    headers = data[0]
    num_cols = len(headers)
    
    # Pad each row to match header length
    padded = [row + [""] * (num_cols - len(row)) for row in data[1:]]
    
    return pd.DataFrame(padded, columns=headers)

def extraction(worksheet_number, cell_values):
    """
    Extract the data from the worksheet.
    Args:
        worksheet_number: The number of the worksheet to get the data from.
        cell_values: The cells to get the data from.
    Returns:
        df: The DataFrame.
    """
    data = get_data(worksheet_number, cell_values)
    df = convert_to_df(data)
    return(df)

def get_all_df():
    """
    Get all the data from the worksheets.
    Returns:
        all_data: A dictionary of the data from the worksheets.
    """
    all_data = {}

    crops = extraction(4,"A2:J15")
    all_data.update({"crops": crops})

    forageables = extraction(6, "A3:E36")
    all_data.update({"forageables": forageables})

    fish = extraction(1, "B2:N85")
    all_data.update({"fish": fish})

    recipes = extraction(7, "B3:U93")
    all_data.update({"recipes": recipes})

    return(all_data)
    


