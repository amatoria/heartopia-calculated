from transform.clean_data import *
from transform.parse_ingredients.parse_ingredients import *
import re

def transform_crops(df):
    df_cleaned = df.copy()

    # Relabel columns to have more conventional naming
    df_cleaned = df_cleaned.rename(columns={
        "Seed Name": "seed_name",
        "Growth Time": "growth_time_minutes",
        "Gardening Lvl": "gardening_level",
        "Seed Sell": "seed_sell",
        "Seed Purchase": "seed_purchase",
        "⭐": "star_1",
        "⭐⭐": "star_2",
        "⭐⭐⭐": "star_3",
        "⭐⭐⭐⭐": "star_4",
        "⭐⭐⭐⭐⭐": "star_5",
    })

    df_cleaned["seed_name"] = df_cleaned["seed_name"].apply(clean_name)
    df_cleaned["growth_time_minutes"] = df_cleaned["growth_time_minutes"].apply(normalize_time)

    numerical_columns = ("gardening_level", "seed_sell", "seed_purchase", "star_1", "star_2", "star_3", "star_4", "star_5")
    
    for column in numerical_columns:
        df_cleaned[column] = df_cleaned[column].apply(normalize_numerical_values)
        
    return df_cleaned

def transform_forageables(df):
    df_cleaned = df.copy()

    # Relabel columns to have more conventional naming
    df_cleaned = df_cleaned.rename(columns={
        "Name": "name",
        "Location/Source": "location_source",
        "Sell Price": "sell_price",
        "Energy Gain": "energy_gain",
        "Buy Price": "buy_price"
    })

    numerical_columns = ["sell_price", "energy_gain", "buy_price"]

    for column in numerical_columns:
        df_cleaned[column] = df_cleaned[column].apply(normalize_numerical_values)

    return df_cleaned

def transform_fish(df):
    df_cleaned = df.copy()

    df_cleaned = df_cleaned.rename(columns={
        "Name": "fish_raw",
        "Location": "location",
        "Fishing Level": "fishing_level",
        "Fish Type": "fish_type",
        "Shadow Size": "shadow",
        "Activity": "activity",
        "Weather": "weather",
        "Time of Day": "time_of_day",
        "⭐": "star_1",
        "⭐⭐": "star_2",
        "⭐⭐⭐": "star_3",
        "⭐⭐⭐⭐": "star_4",
        "⭐⭐⭐⭐⭐": "star_5",        
    })

    # Clean fish names while keeping original column
    df_cleaned.insert(1, "fish_cleaned", '')
    # Add fish notes that were originally included in raw fish names
    df_cleaned.insert(8, "notes", '')

    df_cleaned["fish_cleaned"] = df_cleaned["fish_raw"].apply(get_fish_name)
    df_cleaned["notes"] = df_cleaned["fish_raw"].apply(get_fish_note)

    numerical_columns = ["fishing_level", "star_1", "star_3", "star_4", "star_5"]
    for column in numerical_columns:
        df_cleaned[column] = df_cleaned[column].apply(normalize_numerical_values)

    emoji_columns = ["weather", "time_of_day"]
    for column in emoji_columns:
        df_cleaned[column] = df_cleaned[column].apply(weather_time_emoji_text)

    return df_cleaned


def transform_recipes(df):
    df_cleaned = df.copy()

    # remove fully empty AND blank-string columns
    df_cleaned = df_cleaned.loc[
        :, df_cleaned.astype(str).apply(lambda col: col.str.strip().ne("").any())
    ]

    # flatten columns if needed
    df_cleaned.columns = [str(c).strip() for c in df_cleaned.columns]

    if len(df_cleaned.columns) != 20:
        raise ValueError(
            f"Column mismatch: expected 20, got {len(df_cleaned.columns)}"
        )

    df_cleaned.columns =[
        # Ingredients
        "recipe_name",
        "ingredients_raw",
        "cooking_level",
        "recipe_price",

        # Prices
        "price_star_1",
        "price_star_2",
        "price_star_3",
        "price_star_4",
        "price_star_5",

        # Energy Gained
        "energy_star_1",
        "energy_star_2",
        "energy_star_3",
        "energy_star_4",
        "energy_star_5",

        #Profit
        "cost_to_make",
        "profit_star_1",
        "profit_star_2",
        "profit_star_3",
        "profit_star_4",
        "profit_star_5",
    ]

    # Energy gained and profit will use their respective functions and are therefore not included in numerical values cleaning
    numerical_columns = ["cooking_level", "recipe_price", 
                         "price_star_1", "price_star_2", "price_star_3", "price_star_4", "price_star_5",
                         "profit_star_1", "profit_star_2", "profit_star_3", "profit_star_4", "profit_star_5", 
                         ]
    for column in numerical_columns:
        df_cleaned[column] = df_cleaned[column].apply(normalize_numerical_values)

    df_cleaned["ingredients_parsed"] = df_cleaned["ingredients_raw"].apply(parse_cell)
    return df_cleaned
