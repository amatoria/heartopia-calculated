import re
import unicodedata
import json

def clean_name(name):
    if not name:
        return None

    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    name = name.strip()

    return name

def clean_fish_name(name):
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

def get_fish_name(name):
    return clean_fish_name(name)[0]

def get_fish_note(name):
    return clean_fish_name(name)[1]

def normalize_time(time):
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

def normalize_numerical_values(value):
    if value is None:
        return value
    match = re.search(r"\d+", str(value))
    if not match:
        return None
    return int(match.group())

def weather_time_emoji_text(values):
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

