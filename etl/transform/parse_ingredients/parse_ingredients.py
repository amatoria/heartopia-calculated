import json
import re
from emoji import is_emoji

def recipes_emoji_text(ingredient):
    if ingredient is None:
        return ingredient

    ingredients_map_emojis = {"🍎":{
                    "name": "apple",
                    "type": "ingredient"
                    },
                  "🔵":{
                    "name": "blueberry",
                    "type": "ingredient"
                    },
                  "🍇":{
                    "name": "grape",
                    "type": "ingredient"
                    },
                  "🍊":{
                    "name": "mandarin",
                    "type": "ingredient"
                    },
                  "🍍":{
                    "name": "pineapple",
                    "type": "ingredient"
                    },
                  "🔴":{
                    "name": "raspberry",
                    "type": "ingredient"
                    },
                  "🍓":{
                    "name": "strawberry",
                    "type": "ingredient"
                    },
                  "🍅":{
                    "name": "tomato",
                    "type": "ingredient"
                    },
                  "🥬":{
                    "name": "lettuce",
                    "type": "ingredient"
                    },
                  "🥔":{
                    "name": "potato",
                    "type": "ingredient"
                    },
                  "🌾":{
                    "name": "wheat",
                    "type": "ingredient"
                    },
                  "☕":{
                    "name": "coffee",
                    "type": "ingredient"
                    },
                  "🧀":{
                    "name": "cheese",
                    "type": "ingredient"
                    },
                  "🌽":{
                    "name": "corn",
                    "type": "ingredient"
                    },
                  "🥕":{
                    "name": "carrot",
                    "type": "ingredient"
                    },
                  "🍆":{
                    "name": "eggplant",
                    "type": "ingredient"
                    },
                  "🟤":{
                    "name": "coffee beans",
                    "type": "ingredient"
                    },
                  "🧈":{
                    "name": "butter",
                    "type": "ingredient"
                    },
                  "🍫":{
                    "name": "cocoa",
                    "type": "ingredient"
                    },
                  "🛢️":{
                    "name": "cooking oil",
                    "type": "ingredient"
                    },
                  "🥚":{
                    "name": "egg",
                    "type": "ingredient"
                    },
                  "🥛":{
                    "name": "milk",
                    "type": "ingredient"
                    },
                  "🥩":{
                    "name": "meat",
                    "type": "ingredient"
                    },
                  "🌰":{
                    "name": "truffle",
                    "type": "ingredient"
                    },

                  "❤️":{
                    "name": "red sugar",
                    "type": "ingredient"
                    },
                  "🧡":{
                    "name": "orange sugar",
                    "type": "ingredient"
                    },
                  "💛":{
                    "name": "yellow sugar",
                    "type": "ingredient"
                    },
                  "💜":{
                    "name": "violet sugar",
                    "type": "ingredient"
                    },
                  "💚":{
                    "name": "green sugar",
                    "type": "ingredient"
                    },
                  "💙":{
                    "name": "blue sugar",
                    "type": "ingredient"
                    },
                  "🖤":{
                    "name": "indigo sugar",
                    "type": "ingredient"
                    },
                  "🟫":{
                    "name": "springday brown sugar",
                    "type": "ingredient"
                    },
                  "💃":{
                    "name": "salsa",
                    "type": "ingredient"
                    },
                  "🌳":{
                    "name": "romaine lettuce",
                    "type": "ingredient"
                    },
                  "🟩":{
                    "name": "matcha",
                    "type": "ingredient"
                    },
                  "🌲":{
                    "name": "tea tree",
                    "type": "ingredient"
                    },
                  "🍵":{
                    "name": "tea leaves",
                    "type": "ingredient"
                    },
        
                  # The following emojis considering items in the category (e.g. *any* vegetable)
                  "🥦":{
                    "name": "vegetable",
                    "type": "category"
                    },
                  "🍄":{
                    "name": "mushroom",
                    "type": "category"
                    },
                  "🐟":{
                    "name": "fish",
                    "type": "category"
                    },
                  "🥫":{
                    "name": "jam",
                    "type": "category"
                    },                 
                  "🦞":{
                    "name": "shellfish",
                    "type": "category"
                    },                  
                  "⚪":{
                    "name": "sugar",
                    "type": "category"
                    }
    }

    ingredients_map_text = {
        "white daisy flower":{
            "name": "white daisy flower",
            "type": "ingredient"
        },
        "king crab":{
            "name": "king crab",
            "type": "ingredient",
        },
        "blue european crayfish":{
            "name": "blue european crayfish",
            "type": "ingredient"
        },
        "golden king crab":{
            "name": "golden king crab",
            "type": "ingredient"
        }
    }

    if ingredient not in ingredients_map_emojis:
        return {"name": ingredient,
                "type": "unknown", 
                "note": "token unreadable"}
    ingredients_json = ingredients_map_emojis.get(ingredient)
    return ingredients_json

def parse_cell(text):
    if not text or str(text).strip() == "":
        return None
    
    text = str(text)

    notes = re.findall(r"\((.*?)\)", text)
    notes += re.findall(r"\[(.*?)\]", text)

    clean_text = re.sub(r"\(.*?\)", "", text)
    clean_text = re.sub(r"\[.*?\]", "", clean_text)

    print(clean_text)

    ingredients = []

    if clean_text is None:
        return []
    
    # TODO: add quantity of ingredients
    for c in clean_text:
        emoji_to_text = recipes_emoji_text(c)
        if notes != "" or notes is not None:
            emoji_to_text["note"] = notes
        ingredients.append(emoji_to_text)


    return ingredients