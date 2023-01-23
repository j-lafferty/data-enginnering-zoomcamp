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
    yellow_taxi_header = False
    green_taxi_header = False

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

    if column_headers.count("tpep_pickup_datetime") > 0:
        yellow_taxi_header = True
    elif column_headers.count("lpep_pickup_datetime") > 0:
        green_taxi_header = True

    if yellow_taxi_header:
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    elif green_taxi_header:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    df.to_sql(name=table_name, con=engine, if_exists="append")

    while True:
        t_start = time()

        try:
            df = next(df_iter)

            if yellow_taxi_header:
                df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
                df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            elif green_taxi_header:
                df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
                df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

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
