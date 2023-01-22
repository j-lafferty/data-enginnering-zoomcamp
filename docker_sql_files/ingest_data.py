#!/usr/bin/env python
# coding: utf-8

import argparse
import os
from time import time
import pandas as pd
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = ""

    if url.endswith(".csv.gz"):
        csv_name = "output.csv.gz"
    elif url.endswith(".csv"):
        csv_name = "output.csv"

    # download the csv
    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    df = next(df_iter)
    column_headers = list(df.columns.values)

    try:
        if column_headers.index("tpep_pickup_datetime") and column_headers.index(
            "tpep_dropoff_datetime"
        ):
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    except ValueError:
        pass

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    df.to_sql(name=table_name, con=engine, if_exists="append")

    while True:
        t_start = time()

        try:
            df = next(df_iter)

            try:
                if column_headers.index(
                    "tpep_pickup_datetime"
                ) and column_headers.index("tpep_dropoff_datetime"):
                    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
                    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            except ValueError:
                pass

            df.to_sql(name=table_name, con=engine, if_exists="append")

            t_end = time()

            print(f"Inserted another chunck... took {t_end-t_start} seconds")
        except StopIteration:
            print("Finished ingesting data into postgres")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres.")

    parser.add_argument("--user", help="user name for postgres")
    parser.add_argument("--password", help="password for postgres")
    parser.add_argument("--host", help="host for postgres")
    parser.add_argument("--port", help="port for postgres")
    parser.add_argument("--db", help="database name for postgres")
    parser.add_argument(
        "--table_name", help="name of table where we will write the results"
    )
    parser.add_argument("--url", help="url of csv file")

    args = parser.parse_args()

    main(args)
