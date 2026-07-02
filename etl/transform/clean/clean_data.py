import re
import unicodedata
import json
import pandas as pd
from transform.correct_data_log import correct_data_log
from transform.parse_ingredients.parse_ingredients import parse_energy

def clean_name(name) -> str:
    """
    Clean the name of the item.
    Args:
        name: The name of the item.
    Returns:
        name: The cleaned name of the item.
    """
    if not name:
        return None

    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    name = name.strip()

    return name

def clean_fish_name(name) -> tuple[str, str]:
    """
    Clean the name of the fish.
    Args:
        name: The name of the fish.
    Returns:
        name: The cleaned name of the fish.
    """
    if not name:
        return None
    
    match = re.search(r"\((.*?)\)", name)

    if match:
        note = match.group(1)
    else:
        note = ''

    cleaned_name = re.sub(r"\((.*?)\)", "", name)
    cleaned_name = clean_name(cleaned_name)

    return cleaned_name, note

def get_fish_name(name) -> str:
    """
    Get the name of the fish.
    Args:
        name: The name of the fish.
    Returns:
        name: The name of the fish.
    """
    return clean_fish_name(name)[0]

def get_fish_note(name) -> str:
    """
    Get the note of the fish.
    Args:
        name: The name of the fish.
    Returns:
        note: The note of the fish.
    """
    return clean_fish_name(name)[1]

def get_fish_category(name) -> str:
    """
    Get the category of the fish from its name.
    Args:
        name: The raw or cleaned name of the fish.
    Returns:
        category: One of crab, shrimp, crayfish, lobster, or fish.
    """
    if not name:
        return None

    cleaned = get_fish_name(name)
    if not cleaned:
        return None

    cleaned_lower = cleaned.lower()

    if "crayfish" in cleaned_lower:
        return "crayfish"
    if "crab" in cleaned_lower:
        return "crab"
    if "shrimp" in cleaned_lower or "prawn" in cleaned_lower:
        return "shrimp"
    if "lobster" in cleaned_lower:
        return "lobster"
    return "fish"


def normalize_time(time) -> int:
    """
    Normalize the time to minutes.
    Args:
        time: The time to normalize.
    Returns:
        time: The normalized time in minutes as an integer.
    """
    if not time:
        return None
    time = time.lower().strip()

    match = re.search(r"(\d+)\s*(min|mins|minute|minutes|hour|hours)", time)
    if not match:
        return None
    
    number = int(match.group(1))
    unit = match.group(2)

    if "hour" in unit:
        return number * 60
    
    return number

def normalize_numerical_values(value) -> int:
    """
    Normalize the numerical values.
    Args:
        value: The value to normalize.
    Returns:
        value: The normalized value as an integer.
    """
    if value is None:
        return value
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    return int(match.group())

def weather_time_emoji_text(values) -> list[str]:
    """
    Convert the weather and time of day emojis to text.
    Args:
        values: The values to convert.
    Returns:
        values_text: The converted values as a list of strings.
    """
    if values is None:
        return values
    
    values_text = []
    for value in values:
        match value:
            case "🌞":
                values_text.append("sunny")
            case "🌧️":
                values_text.append("precipitation")
            case "🌈":
                values_text.append("rainbow")
            case "🌙":
                values_text.append("dusk")
            case "🌅":
                values_text.append("afternoon")
            case "☀️":
                values_text.append("morning")
            case "🌇":
                values_text.append("dawn")
    return values_text

def fix_blue_european_crayfish_sashimi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive Blue European Crayfish Sashimi's recipe_price and energy values
    from Crayfish Sashimi: same price, 2x energy gained per star level.
    """
    df_corrected = df.copy()

    source_mask = df_corrected["recipe_name"] == "Crayfish Sashimi"
    target_mask = df_corrected["recipe_name"] == "Blue European Crayfish Sashimi"

    if not source_mask.any() or not target_mask.any():
        print("Warning: source or target row not found for crayfish sashimi correction")
        return df_corrected

    source = df_corrected.loc[source_mask].iloc[0]    
    energy_columns = ["energy_star_1", "energy_star_2", "energy_star_3", "energy_star_4", "energy_star_5"]

    for i in df_corrected.loc[target_mask].index:
        correct_data_log(
            table_name="recipes",
            row_key="Blue European Crayfish Sashimi",
            column_name="recipe_price",
            original_value=None,
            corrected_value=source["recipe_price"],
            reason="Missing recipe_price; derived as same as Crayfish Sashimi",
            source="Crayfish Sashimi entry",
        )
        df_corrected.at[i, "recipe_price"] = int(source["recipe_price"])

        for column in energy_columns:
            parsed_energy = parse_energy(source[column])
            corrected = int(parsed_energy * 2)
            correct_data_log(
                table_name="recipes",
                row_key="Blue European Crayfish Sashimi",
                column_name=column,
                original_value=None,
                corrected_value=corrected,
                reason="Missing energy value; derived as 2x Crayfish Sashimi",
                source="calculated",
            )
            df_corrected.at[i, column] = corrected

    return df_corrected

def fix_milkshake_recipe_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive recipe prices that use the Milkshake recipe as its base.
    """
    
    df_corrected = df.copy()
    source_mask = df_corrected["recipe_name"] == "Milkshake (Regular)"
    target_mask = df_corrected["recipe_name"].str.startswith("Milkshake (") & (df_corrected["recipe_name"] != "Milkshake(Regular)")

    if not source_mask.any() or not target_mask.any():
        print("Warning: source or target row not found for milkshake correction")
        return df_corrected

    source = df_corrected.loc[source_mask].iloc[0]

    for i in df_corrected.loc[target_mask].index:
        correct_data_log(
            table_name="recipes",
            row_key=df_corrected.at[i, "recipe_name"],
            column_name="recipe_price",
            original_value=int(df_corrected.at[i, "recipe_price"]),
            corrected_value=source["recipe_price"],
            reason="Missing recipe_price; derived as same as Milkshake",
            source="Milkshake recipe",
        )
        df_corrected.at[i, "recipe_price"] = source["recipe_price"]

    return df_corrected

def normalize_recipe_price(df: pd.DataFrame) -> pd.DataFrame:
    df_corrected = df.copy()

    blank_mask = df_corrected["recipe_price"].isna() | (df_corrected["recipe_price"].astype(str).str.strip() == "")

    for i in df_corrected.loc[blank_mask].index:
        correct_data_log(
            table_name="recipes",
            row_key=df_corrected.at[i, "recipe_name"],
            column_name="recipe_price",
            original_value=df_corrected.at[i, "recipe_price"],
            corrected_value=0,
            reason="Normalize free recipe price",
            source="calculated",
        )
        df_corrected.at[i, "recipe_price"] = 0

    return df_corrected

def clean_recipes_table(df: pd.DataFrame) -> pd.DataFrame:
    df_corrected = df.copy()
    df_corrected = normalize_recipe_price(df_corrected)
    df_corrected = fix_blue_european_crayfish_sashimi(df_corrected)
    df_corrected = fix_milkshake_recipe_prices(df_corrected)
    return df_corrected

