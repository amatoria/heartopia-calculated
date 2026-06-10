import json
import re
from emoji import is_emoji
from transform.parse_ingredients.ingredients_map import INGREDIENTS_MAP_EMOJIS, INGREDIENTS_MAP_TEXT

def count_ingredients(clean_text):
    if clean_text is None:
        return {}
    
    ingredients_qty = {}

    for key,value in INGREDIENTS_MAP_EMOJIS.items():
        occurrences = clean_text.count(key)

        if occurrences:
            ingredients_qty[key] = occurrences
    return ingredients_qty

def parse_ingredients(ingredients_qty):
    ingredient_entries = []
    for ingredient, qty in ingredients_qty.items():
      ingredient_entry = {}
      ingredient_info = INGREDIENTS_MAP_EMOJIS[ingredient]

      ingredient_entry["name"] = ingredient_info["name"]
      ingredient_entry["type"] = ingredient_info["type"]
      ingredient_entry["quantity"] = ingredients_qty[ingredient]
      ingredient_entries.append(ingredient_entry)

    return ingredient_entries

def parse_notes(notes):
    if notes is None or notes == "":
        return None
    
    return notes

def parse_cell(text):
    if not text or str(text).strip() == "":
        return None
    
    text = str(text)

    notes = re.findall(r"\((.*?)\)", text)
    notes += re.findall(r"\[(.*?)\]", text)

    clean_text = re.sub(r"\(.*?\)", "", text)
    clean_text = re.sub(r"\[.*?\]", "", clean_text)

    print(clean_text)

    tokens = []
    ingredients = []

    if clean_text is None:
        return []
    
    ingredients_qty = count_ingredients(clean_text)
    print(ingredients_qty)
    ingredients_entries = parse_ingredients(ingredients_qty)
    print(ingredients_entries)
    # print(notes)
    # return ingredients