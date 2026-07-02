from extract.sheets_to_df import get_all_df
from transform.transform_data import *
from load.postgres_loader import df_to_sql, get_engine
import logging
import utils.logging_config

def run_pipeline():
    # Extract
    dfs = get_all_df()
    logging.info("Data extracted from Google Sheets.")

    # Transform
    raw_df_crops = dfs["crops"]
    cleaned_df_crops = transform_crops(raw_df_crops)

    raw_df_forageables = dfs["forageables"]
    cleaned_df_forageables = transform_forageables(raw_df_forageables)

    raw_df_fish = dfs["fish"]
    cleaned_df_fish = transform_fish(raw_df_fish)

    raw_df_recipes = dfs["recipes"]
    cleaned_df_recipes = clean_recipes_table(transform_recipes(raw_df_recipes))

    # Load
    logging.info("Creating engine...")
    engine = get_engine()

    with engine.connect() as conn:
        logging.info("Engine connected.")

    for table_name, df in dfs.items():
        df_to_sql(table_name,df,engine)

    df_to_sql("crops", cleaned_df_crops, engine)
    df_to_sql("forageables", cleaned_df_forageables, engine)
    df_to_sql("fish", cleaned_df_fish, engine)
    df_to_sql("recipes", build_recipes_table(cleaned_df_recipes), engine)
    df_to_sql("ingredients", build_ingredient_table(cleaned_df_recipes), engine)
    df_to_sql("fish", build_fish_main_table(cleaned_df_fish), engine)
    df_to_sql("fish_weather", build_fish_weather_table(cleaned_df_fish), engine)
    df_to_sql("fish_time_of_day", build_fish_time_of_day_table(cleaned_df_fish), engine)

    df_to_sql("correction_log", build_correction_table(), engine)

    logging.info("ETL complete.")

if __name__ == "__main__":
    run_pipeline()
