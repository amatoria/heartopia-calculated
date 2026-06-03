import os
from dotenv import load_dotenv
import logging

import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from sqlalchemy.types import JSON

load_dotenv()

def get_engine():
    DB_USER= os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")

    return create_engine(f"postgresql+psycopg2://"
                        f"{DB_USER}:{DB_PASSWORD}"
                        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}")


def df_to_sql(table_name, df, engine):

    if df is None:
        raise ValueError(f"{table_name} DataFrame is None.")

    #Create a table for PostgreSQL
    logging.info(f"Loading table \"{table_name}\" into Postgres...")
    
    df_data_only = df.iloc[1:]

    sql_data = df_data_only.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        dtype={"ingredients_parsed": JSON()}
    )
