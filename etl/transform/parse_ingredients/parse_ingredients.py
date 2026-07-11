import re
from emoji import is_emoji
from transform.parse_ingredients.ingredients_map import *
import pandas as pd

_WORD_NUMBERS = {
  "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
  "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

def _resolve_emoji(emoji: str) -> str:
  """
  Finds the ingredient name of an emoji.

  Args:
    emoji: The emoji whose name is to be found
  Returns:
    string of the ingredient name for an emoji, or the raw emoji if not in map
  """
  info = INGREDIENTS_MAP_EMOJIS.get(emoji)
  return info["name"] if info else emoji


def _extract_resolved(text: str) -> list[str]:
  """
  Identifies emojis in a given string to parse into ingredient name.

  Args:
    text: The string in which to parse for emojis
  Returns:
    list of resolved ingredient names for every emoji in text
  """
  return [_resolve_emoji(ch) for ch in text if is_emoji(ch)]

def _group_emoji_runs(names: list[str]) -> list[dict]:
  """
  Groups emoji runs into choices.

  Args:
    names: The list of ingredient names to group
  Returns:
    list of choices, each with a count and options
  """
  choices = []
  for name in names:
      if choices and choices[-1]["options"] == [name]:
          choices[-1]["count"] += 1
      else:
          choices.append({"count": 1, "options": [name]})
  return choices

def _parse_quantity_prefix(text: str) -> tuple[int | None, str]:
  """
  Extract a leading count from text,
    e.g.  "Any of the four ...", "Two fruit ...", "3 Golden King Crabs ..."

  Args:
    text: The string of text that may contain a quantity prefix
  Returns:
    tuple of (count, remainder) or (None, original_text)
  """
  text = text.strip()

  # "Any of the <word|digit>"
  m = re.match(r"any(?:\s+of)?(?:\s+the)?\s+(\w+)", text, re.IGNORECASE)
  m = re.match(r"any(?:\s+of)?(?:\s+the)?\s+(\w+)", text, re.IGNORECASE)
  if m:
      word = m.group(1).lower()
      count = _WORD_NUMBERS.get(word) or (int(word) if word.isdigit() else None)
      if count is not None:               # only consume prefix if we got a real number
          return count, text[m.end():].strip()

  # Leading digit: "3 Golden King Crabs"
  m = re.match(r"(\d+)\s+", text)
  if m:
      return int(m.group(1)), text[m.end():].strip()

  # Leading word-number: "Two fruit"
  m = re.match(r"(\w+)\b", text)
  if m:
      word = m.group(1).lower()
      if word in _WORD_NUMBERS:
          return _WORD_NUMBERS[word], text[m.end():].strip()

  return None, text


def _resolve_text_ingredients(text: str) -> list[dict]:
    """
    Formats the cell such that each recipe's ingredients and ingredient quality is listed, such as:

        [{count: 4, options: {apple, blueberry, raspberry, mandarin}]

    Args:
      text: The string of ingredients to convert
    Returns:
      list of each ingredient choice and the quantity required
    """
    choices = []
    remainder = text

    for key in sorted(INGREDIENTS_MAP_TEXT, key=len, reverse=True):
        pattern = re.compile(re.escape(key), re.IGNORECASE)
        if not pattern.search(remainder):
            continue

        count_match = re.search(rf"(\d+)\s+{re.escape(key)}", remainder, re.IGNORECASE)
        qty = int(count_match.group(1)) if count_match else 1

        name = INGREDIENTS_MAP_TEXT[key]["name"]

        # If this is a category, expand to all valid options
        if name in CATEGORY_EXPANSIONS:
            choices.append({
                "count": qty,
                "options": CATEGORY_EXPANSIONS[name],
            })
        else:
            choices.append({
                "count": qty,
                "options": [name],
            })

        remainder = pattern.sub("", remainder)
        if count_match:
            remainder = remainder.replace(count_match.group(1), "", 1)

    return choices

def parse_cost(value) -> tuple[float | None, float | None]:
    """'300-460' → (300, 460), '475' → (475, 475), blank → (None, None)"""
    s = str(value).strip()
    if not s or s in ("nan", ""):
        return None, None
    m = re.match(r"([\d.]+)\s*-\s*([\d.]+)", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.match(r"([\d.]+)", s)
    if m:
        v = float(m.group(1))
        return v, v
    return None, None


def parse_energy(value) -> int | None:
    """'+35 (Energy Buff)' → 35, blank → None"""
    s = str(value).strip()
    if not s or s in ("nan", ""):
        return None
    m = re.search(r"[+-]?([\d.]+)", s)
    return int(m.group(1)) if m else None

def parse_cell(text) -> list[dict] | None:
    if not text or str(text).strip() == "":
        return None

    text = str(text).strip()

    paren_contents = re.findall(r"\(([^)]*)\)", text)
    paren_pools = [_extract_resolved(m) for m in paren_contents if _extract_resolved(m)]

    clean = re.sub(r"\(.*?\)", "", text)
    clean = re.sub(r"\[.*?\]", "", clean).strip()

    text_parts = []
    emoji_list = []

    for token in re.findall(r"\S+", clean):
        token_emojis = _extract_resolved(token)
        if token_emojis:
            emoji_list += token_emojis
        elif token not in ("+", "&"):
            text_parts.append(token)

    combined_text = " ".join(text_parts).strip()

    paren_text_choices = []
    for paren in paren_contents:
        segments = [s.strip() for s in paren.split(";")]
        for segment in segments:
            if not _extract_resolved(segment):
                paren_text_choices += _resolve_text_ingredients(segment)

    count, _ = _parse_quantity_prefix(combined_text)
    is_choice_line = count is not None and bool(emoji_list or paren_pools)

    choices = []

    if is_choice_line:
        option_pool = paren_pools[0] if paren_pools else emoji_list
        choices.append({"count": count, "options": option_pool})
        pool_set = set(option_pool)
        fixed = [e for e in emoji_list if e not in pool_set]
        choices += _group_emoji_runs(fixed)
    else:
        choices += _group_emoji_runs(emoji_list)
        segments = [s.strip() for s in combined_text.split(",")]
        for segment in segments:
            choices += _resolve_text_ingredients(segment)

    choices += paren_text_choices

    return choices if choices else None