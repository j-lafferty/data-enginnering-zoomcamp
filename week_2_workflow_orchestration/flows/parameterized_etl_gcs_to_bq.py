from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(retries=3)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../data/")
    return Path(f"../data/{gcs_path}")


@task()
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to Big Query"""

    gcp_credentials_block = GcpCredentials.load("zoom-gcp-redits")

    df.to_gbq(
        destination_table="trips_data_all.yellow_trip_data",
        project_id="ny-rides-jl",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )


@flow(log_prints=True)
def etl_gcs_to_bq(months: list[int] = [1, 2], year: int = 2021, color: str = "yellow"):
    """Main ETL flowto load data into Big Query"""
    total_rows = 0

    for month in months:
        path = extract_from_gcs(color, year, month)
        df = pd.read_parquet(path)
        write_bq(df)
        total_rows += len(df)

    print(f"total rows processed: {total_rows}")


if __name__ == "__main__":
    color = "yellow"
    months = [2, 3]
    year = 2019
    etl_gcs_to_bq(months, year, color)
