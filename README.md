# Heartopia Data Pipeline & Profitability Analysis

An end-to-end ETL pipeline and interactive Tableau dashboard that answers the question: **which recipes should a player prioritize to maximize profit given their current level and available ingredients?**

Built with Python, PostgreSQL, Docker, and Tableau.

---

## Live Dashboard

[View on Tableau Public](https://public.tableau.com/app/profile/tora.tran/viz/heartopia_extract/RecipeProfitability) 

---

## Screenshots

### Profitable Recipes by Effective Level
<img width="425" height="344" alt="image" src="https://github.com/user-attachments/assets/b3f01eaa-ccd2-41ad-9a24-2ecb66edd12d" />


### Best Recipe per Crop
<img width="392" height="319" alt="image" src="https://github.com/user-attachments/assets/f0fa0149-6b6d-4e17-b763-9b9208250f92" />


### Jam Profits (Crop-Based)
<img width="524" height="627" alt="image" src="https://github.com/user-attachments/assets/0cbe7fc5-6932-4ce7-94f5-9c500a7865e8" />


### Ingredient Frequency in High-Profit Recipes
<img width="471" height="745" alt="image" src="https://github.com/user-attachments/assets/ed074e9d-ee8f-46d6-905e-8f2a0ca6f643" />


---

## Project Overview

The raw data lives in a collaboratively maintained Google Sheets document.
The pipeline extracts it via the Google Sheets API, cleans and transforms it
in Python, loads it into a normalized PostgreSQL database running in Docker,
and feeds it into Tableau for visualization.

```
Google Sheets
      |
Google Sheets API (gspread)
      |
Python ETL (pandas, SQLAlchemy)
      |
PostgreSQL (Docker)
      |
Tableau
```

---

## Pipeline Architecture

### Extraction
Raw data is pulled from Google Sheets using `gspread` and converted into
pandas DataFrames. Rows are padded to handle the Google Sheets API's
behavior of truncating trailing empty cells.

### Transformation

**Cleaning**
Each table has a dedicated `transform_` function handling:
- Column renaming to snake_case
- Time normalization (`15 min`, `1 hour` → integer minutes)
- Numerical value cleaning (stripping annotations like `540 (+ bonus)`)
- Fish name separation into canonical name and notes columns

**Recipe Ingredient Parsing**
The most complex transformation in the pipeline. Raw ingredient cells
contain a mix of emojis, free text, choice constraints, and sub-recipe
references:

```
🍎🍎🍎🍎
🦞🦞 (King Crab only)
Two fruit (🍎🔵🍇🍊...) + 🥛🥛
Any of the four 🍎🔵🍇🍊🍍🔴🍓🍅
2 Cheesecake, 2 Mellow Black Tea
(Tiramisu; any fruit/vegetables)
```

A custom `parse_cell()` function resolves each cell into a unified list
of choice objects:

```python
{"count": N, "options": ["ingredient_name", ...]}
```

Fixed ingredients are modeled as choices with a single option, keeping
the output shape consistent regardless of cell complexity. Emojis are
resolved to ingredient names via a lookup map. Text ingredients
(including sub-recipe references) are matched against a separate text map.

**Correction Layer**
A correction log tracks every value changed during the pipeline:
- **Derived corrections** — values computed from other columns
  (e.g. `seed_sell = seed_purchase / 2` when blank)
- **Manual corrections** — sourced from `manual_corrections.csv`,
  an external file of known data gaps filled from the game wiki
- **Recipe-specific corrections** — derived corrections for recipes
  whose prices or energy values are based on a parent recipe
  (e.g. all Milkshake variants derive their price from Milkshake Regular)

Every correction is logged with: `table_name`, `row_key`, `column`,
`original_value`, `corrected_value`, `reason`, `source`.

### Loading
Cleaned DataFrames are written to PostgreSQL using SQLAlchemy.
PostgreSQL runs in a Docker container for portability.

---

## Schema

```
recipes
  recipe_name, cooking_level, recipe_price, cost_to_make,
  price_star_1..5, energy_star_1..5, profit_star_1..5,
  is_high_profit

recipe_ingredients
  recipe_name, ingredient, type, quantity,
  choice_group, choice_pick_count, source

crops
  seed_name, growth_time_minutes, gardening_level,
  seed_sell, seed_purchase, star_1..5, source

fish
  fish_id, fish_cleaned, location, fishing_level,
  fish_type, shadow, activity, category, star_1..5, source

fish_weather
  fish_id, weather

fish_time_of_day
  fish_id, time_of_day

forageables
  name, location_source, sell_price, energy_gain, buy_price, source

correction_log
  table_name, row_key, column_name,
  original_value, corrected_value, reason, source
```

**Key design decisions:**
- `recipe_ingredients` uses `choice_group` and `choice_pick_count` to
  model player choice slots without a separate junction table
- `type` on `recipe_ingredients` distinguishes raw ingredients
  (`ingredient`), category slots (`category`), and sub-recipe
  dependencies (`recipe`, `recipe_category`)
- `is_high_profit` is computed in the ETL (75th percentile of
  `profit_star_1`) rather than Tableau, since `PERCENTILE()` is
  unavailable on live database connections
- `fish_weather` and `fish_time_of_day` are exploded from multi-value
  columns using pandas `.explode()` for clean relational modeling

---

## Tableau Dashboard

The dashboard answers five questions:

| Sheet | Question |
|---|---|
| Profitable Recipes by Effective Level | What is the best recipe I can make right now? |
| Best Recipe per Ingredient | What should I cook with what I am already growing? |
| Profit per Minute (Crops) | Which recipe gives the best return on farming time? |
| Jam Profits | Which jam should I make? |
| Ingredient Frequency in High-Profit Recipes | Which ingredients are worth prioritizing? |

**Effective Level** is a calculated field combining cooking level,
gardening level of crop ingredients, and fishing level of fish
ingredients — giving a more accurate picture of when a recipe actually
becomes available to a player than cooking level alone.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data source | Google Sheets (gspread) |
| Transformation | Python 3, pandas, regex |
| Database ORM | SQLAlchemy |
| Database | PostgreSQL 16 |
| Containerization | Docker |
| Visualization | Tableau |

---

## Repository Structure

```
heartopia-etl/
├── etl/
│   ├── extract/
│   │   └── sheets_to_df.py       # Google Sheets extraction
│   ├── load/
│   │   ├── postgres_loader.py    # Load DataFrames into Postgres
│   ├── transform/
│   │   ├── clean/
│   │   │   └── clean_data.py     # correction functions
│   │   ├── transform.py          # transform_ functions per table

│   │   └── parse_ingredients/
│   │       ├── parse_ingredients.py   # parse_cell() and helpers
│   │       └── ingredients_map.py     # emoji and text ingredient maps
│   ├── correct_data.py           # correction log
│   ├── correct_data_log.py       # correction logger
│   └── main.py                   # pipeline entry point
└── README.md
```
