import gspread
import pandas as pd

gc = gspread.service_account()
sheet = gc.open("Copy of Heartopia Guide - updated April 21st")


def get_data(worksheet_number, cell_values):
    return sheet.get_worksheet(worksheet_number).get(cell_values)

def convert_to_df(data):
    df = pd.DataFrame(data, columns=data[0])
    return(df)

def extraction(worksheet_number, cell_values):
    data = get_data(worksheet_number, cell_values)
    df = convert_to_df(data)
    return(df)

def get_all_df():
    all_data = {}

    crops = extraction(4,"A2:J15")
    all_data.update({"crops": crops})

    forageables = extraction(6, "A3:E36")
    all_data.update({"forageables": forageables})

    fish = extraction(1, "B2:N85")
    all_data.update({"fish": fish})

    recipes = extraction(7, "B3:U93")
    all_data.update({"recipes": recipes})

    # ingredients = extraction(7, "AB12:AD57")
    # all_data.update({"ingredients": ingredients})

    return(all_data)
    


