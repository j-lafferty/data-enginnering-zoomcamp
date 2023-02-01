# Data Engineering ZoomCamp - Week 2 Homework
[Week 2 Homework](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2023/week_2_workflow_orchestration/homework.md)


## Question 1. Load January 2020 data
> Using the etl_web_to_gcs.py flow that loads taxi data into GCS as a guide, create a flow that loads the green taxi CSV dataset for January 2020 into GCS and run it. Look at the logs to find out how many rows the dataset has.
> 
> How many rows does that dataset have?
> 
> - 447,770
> - 766,792
> - 299,234
> - 822,132

I updated the `etl_web_to_gcs.py` script to the following:
```
from pathlib import Path
import pandas as pd
import fnmatch
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket


@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""

    df = pd.read_csv(dataset_url)
    return df


@task(log_prints=True)
def clean(df=pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    pickup_datetime = "".join(fnmatch.filter(df, "?pep_pickup_datetime"))
    dropoff_datetime = "".join(fnmatch.filter(df, "?pep_dropoff_datetime"))

    df[pickup_datetime] = pd.to_datetime(df[pickup_datetime])
    df[dropoff_datetime] = pd.to_datetime(df[dropoff_datetime])

    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df


@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    path = f"data/{color}/{dataset_file}.parquet"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, compression="gzip")
    return path


@task()
def write_gcs(path: Path) -> None:
    """Uploading local parquet file to GCS"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("zoom-gcs")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=f"{path}", to_path=path)
    return


@flow()
def etl_web_to_gcs() -> None:
    """The main ETL function"""
    color = "green"
    year = 2020
    month = 1
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)


if __name__ == "__main__":
    etl_web_to_gcs()
```
I then opened two terminal windows and activated the same `conda environment` in both windows.

In one window, I started the `Orion server` with:
```
prefect orion start
```
In the other window, I executed the python script with:
```
python flows/etl_web_to_gcs.py
```
As prefect was running the flow and tasks, the log printed: 
```
23:27:00.198 | INFO    | Task run 'clean-b9fd7e03-0' - rows: 447770
```


## Question 2. Scheduling with Cron
> Cron is a common scheduling specification for workflows.
> 
> Using the flow in etl_web_to_gcs.py, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?
> 
> - 0 5 1 * *
> - 0 0 5 1 *
> - 5 * 1 0 *
> - * * 5 1 0

The unix-cron string format is a set of five fields in a line, which indicates the `Minute Hour Day_of_Month Month Day_of_week`.

The time fields have the following format and possible values, and must follow this order:
```
Field	            Format of valid values
Minute	            0-59
Hour	            0-23
Day of the month	1-31
Month	            1-12 (or JAN to DEC)
Day of the week	    0-6 (or SUN to SAT; or 7 for Sunday)
```
- A field can contain an asterisk (`*`), which always stands for "first-last".
- The default time zone is set to `Etc/UTC`.

So, to create a deployment as requested in this question, the following terminal command would be use:
```
prefect deployment build flows/etl_web_to_gcs.py:etl_web_to_gcs -n etl_green --cron "0 5 1 * *" -a
```


## Question 3. Loading data to BigQuery
> Using etl_gcs_to_bq.py as a starting point, modify the script for extracting data from GCS and loading it into BigQuery. This new script should not fill or remove rows with missing values. (The script is really just doing the E and L parts of ETL).
> 
> The main flow should print the total number of rows processed by the script. Set the flow decorator to log the print statement.
> 
> Parametrize the entrypoint flow to accept a list of months, a year, and a taxi color.
> 
> Make any other necessary changes to the code for it to function as required.
> 
> Create a deployment for this flow to run in a local subprocess with local flow code storage (the defaults).
> 
> Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS. Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?
> 
> - 14,851,920
> - 12,282,990
> - 27,235,753
> - 11,338,483


## Question 4. Github Storage Block
> Using the web_to_gcs script from the videos as a guide, you want to store your flow code in a GitHub repository for collaboration with your team. Prefect can look in the GitHub repo to find your flow code and read it. Create a GitHub storage block from the UI or in Python code and use that in your Deployment instead of storing your flow code locally or baking your flow code into a Docker image.
> 
> Note that you will have to push your code to GitHub, Prefect will not push it for you.
> 
> Run your deployment in a local subprocess (the default if you don’t specify an infrastructure). Use the Green taxi data for the month of November 2020.
> 
> How many rows were processed by the script?
> 
> - 88,019
> - 192,297
> - 88,605
> - 190,225


## Question 5. Email or Slack notifications
> Q5. It’s often helpful to be notified when something with your dataflow doesn’t work as planned. Choose one of the options below for creating email or slack notifications.
> 
> The hosted Prefect Cloud lets you avoid running your own server and has Automations that allow you to get notifications when certain events occur or don’t occur.
> 
> Create a free forever Prefect Cloud account at app.prefect.cloud and connect your workspace to it following the steps in the UI when you sign up.
> 
> Set up an Automation that will send yourself an email when a flow run completes. Run the deployment used in Q4 for the Green taxi data for April 2019. Check your email to see the notification.
> 
> Alternatively, use a Prefect Cloud Automation or a self-hosted Orion server Notification to get notifications in a Slack workspace via an incoming webhook.
> 
> Join my temporary Slack workspace with this link. 400 people can use this link and it expires in 90 days.
> 
> In the Prefect Cloud UI create an Automation or in the Prefect Orion UI create a Notification to send a Slack message when a flow run enters a Completed state. Here is the Webhook URL to use: https://hooks.slack.com/services/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
> 
> Test the functionality.
> 
> Alternatively, you can grab the webhook URL from your own Slack workspace and Slack App that you create.
> 
> How many rows were processed by the script?
> 
> - 125,268
> - 377,922
> - 728,390
> - 514,392


## Question 6. Secrets
> Prefect Secret blocks provide secure, encrypted storage in the database and obfuscation in the UI. Create a secret block in the UI that stores a fake 10-digit password to connect to a third-party service. Once you’ve created your block in the UI, how many characters are shown as asterisks (*) on the next page of the UI?
> 
> - 5
> - 6
> - 8
> - 10
