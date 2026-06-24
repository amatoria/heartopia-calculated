from transform.clean_data import *
from transform.parse_ingredients.parse_ingredients import *
import re
from transform.parse_ingredients.parse_ingredients import parse_cost, parse_energy
from transform.correct_data import *

def transform_crops(df):
    """
    Transform the crops data.
    Args:
        df: The raw crops data.
    Returns:
        df_cleaned: The cleaned crops data.
    """
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

    df_cleaned["notes"] = ""

    df_cleaned["seed_name"] = df_cleaned["seed_name"].apply(clean_name)
    df_cleaned["growth_time_minutes"] = df_cleaned["growth_time_minutes"].apply(normalize_time)

    numerical_columns = ("gardening_level", "seed_sell", "seed_purchase", "star_1", "star_2", "star_3", "star_4", "star_5")
    
    for column in numerical_columns:
        df_cleaned[column] = df_cleaned[column].apply(normalize_numerical_values)
    
    df_cleaned = correct_crops_data(df_cleaned)
            
    return df_cleaned

def transform_forageables(df):
    """
    Transform the forageables data.
    Args:
        df: The raw forageables data.
    Returns:
        df_cleaned: The cleaned forageables data.
    """
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

def build_fish_weather_table(df: pd.DataFrame) -> pd.DataFrame:
    fish_weather = df[["fish_id", "weather"]].explode("weather").dropna(subset=["weather"]).reset_index(drop=True)    
    return fish_weather

def build_fish_time_of_day_table(df: pd.DataFrame) -> pd.DataFrame:
    fish_time_of_day = df[["fish_id", "time_of_day"]].explode("time_of_day").dropna(subset=["time_of_day"]).reset_index(drop=True)
    return fish_time_of_day

def build_fish_main_table(df):
    fish_main = df.drop(columns=["weather", "time_of_day"])
    return fish_main

def transform_fish(df):
    """
    Transform the fish data.
    Args:
        df: The raw fish data.
    Returns:
        df_cleaned: The cleaned fish data.
    """
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

    df_cleaned = df_cleaned.reset_index(drop=True)
    df_cleaned.insert(0, "fish_id", df_cleaned.index + 1)

    df_cleaned["category"] = df_cleaned["fish_cleaned"].apply(get_fish_category)

    return df_cleaned

def build_recipe_table(df_cleaned: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for r, row in df_cleaned.iterrows():
        cost_min, cost_max = parse_cost(row["cost_to_make"])

        rows.append({
            "recipe_name":    row["recipe_name"],
            "cooking_level":  row["cooking_level"],
            "recipe_price":   row["recipe_price"] if str(row["recipe_price"]).strip() not in ("", "nan") else None,
            "cost_min":       cost_min,
            "cost_max":       cost_max,
            "price_star_1":   row["price_star_1"],
            "price_star_2":   row["price_star_2"],
            "price_star_3":   row["price_star_3"],
            "price_star_4":   row["price_star_4"],
            "price_star_5":   row["price_star_5"],
            "energy_star_1":  parse_energy(row["energy_star_1"]),
            "energy_star_2":  parse_energy(row["energy_star_2"]),
            "energy_star_3":  parse_energy(row["energy_star_3"]),
            "energy_star_4":  parse_energy(row["energy_star_4"]),
            "energy_star_5":  parse_energy(row["energy_star_5"]),
            "profit_star_1":  row["profit_star_1"],
            "profit_star_2":  row["profit_star_2"],
            "profit_star_3":  row["profit_star_3"],
            "profit_star_4":  row["profit_star_4"],
            "profit_star_5":  row["profit_star_5"],
        })

    return pd.DataFrame(rows)

def build_ingredient_table(df_cleaned: pd.DataFrame) -> pd.DataFrame:
    """
    For each recipe, parse the ingredients cell and explode into one row
    per ingredient option, with choice_group and choice_pick_count.

    Output columns:
        recipe_name, ingredient, type, quantity,
        choice_group, choice_pick_count
    """
    rows = []

    for _, row in df_cleaned.iterrows():
        recipe_name = row["recipe_name"]
        parsed = parse_cell(row["ingredients_raw"])

        if not parsed:
            # Unparseable cell (e.g. pure text note) — still emit a sentinel
            # row so the recipe isn't silently absent from the ingredient table
            rows.append({
                "recipe_name":       recipe_name,
                "ingredient":        None,
                "type":              None,
                "quantity":          None,
                "choice_group":      None,
                "choice_pick_count": None,
            })
            continue

        choice_group_counter = 1

        for choice in parsed:
            options = choice["options"]
            count   = choice["count"]
            is_choice = len(options) > 1

            choice_group      = choice_group_counter if is_choice else None
            choice_pick_count = count if is_choice else None

            for option in options:
                # Resolve type from either map
                ingredient_type = None
                for emoji, info in INGREDIENTS_MAP_EMOJIS.items():
                    if info["name"] == option:
                        ingredient_type = info["type"]
                        break
                if ingredient_type is None and option in INGREDIENTS_MAP_TEXT:
                    ingredient_type = INGREDIENTS_MAP_TEXT[option]["type"]

                rows.append({
                    "recipe_name":       recipe_name,
                    "ingredient":        option,
                    # fixed ingredients carry their count in quantity;
                    # choice ingredients always contribute 1 slot per option
                    "quantity":          count if not is_choice else 1,
                    "type":              ingredient_type,
                    "choice_group":      choice_group,
                    "choice_pick_count": choice_pick_count,
                })

            if is_choice:
                choice_group_counter += 1

    return pd.DataFrame(rows)

def transform_recipes(df):
    """ 
    Transform the recipes data.
    Args:
        df: The raw recipes data.
    Returns:
        df_cleaned: The cleaned recipes data.
    """
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

    df_cleaned["ingredient_parsed"] = df_cleaned["ingredients_raw"].apply(parse_cell)
    return df_cleaned
