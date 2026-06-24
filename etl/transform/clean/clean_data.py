import re
import unicodedata
import json

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

