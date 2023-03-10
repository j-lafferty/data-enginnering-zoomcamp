# Data Engineering ZoomCamp - Week 1 Homework
[Week 1 Homework](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2023/week_1_docker_sql/homework.md)


## Question 1. Knowing docker tags
> Which tag has the following text? - Write the image ID to the file
>
> - --imageid string
> - --iidfile string
> - --idimage string
> - --idfile string

We're looking for a tag associated with a command that writes an image.

By typing `docker --help` we will find one docker command that does this:
```
build       Build an image from a Dockerfile
```

We can now lookup the differnt tags associated with `docker build` by typing `docker build --help`. Doing so, we will find that the answer to this question is:
```
--iidfile string          Write the image ID to the file
```


## Question 2. Understanding docker first run
> Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash. Now check the python modules that are installed ( use pip list). How many python packages/modules are installed?
>
> - 1
> - 6
> - 3
> - 7

We can simply use the `docker run` command with the options `-i` for interactive and `-t` for tty (terminal access).

We will also need to specify the python version for our image by using `python:3.9`.

Finally, we will need to override the default entrypoint of the python container to bash by using `--entrypoint=bash`.

So, the final docker command we will use is:
```
docker run -it --entrypoint=bash python:3.9
```
Once the container is running we can execute the bash command: `pip list`

The command should return the following list of installed python packages/modules:
```
Package    Version
---------- -------
pip        22.0.4
setuptools 58.1.0
wheel      0.38.4
```
So, the answer to this question is there are **_3 installed python packages/modules_**.


## Question 3. Count records
**We will use the green taxi trips data from January 2019 and the zones data**

Green taxi trips data:
```
https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz
```
Zones data:
```
https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```
> How many taxi trips were totally made on January 15?
> 
> Tip: started and finished on 2019-01-15.
> 
> Remember that `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns are in the format timestamp (date and hour+min+sec) and not in date.
> 
> - 20689
> - 20530
> - 17630
> - 21090

We will need to update the `ingest_data.py` script to convert the `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns to date format. We could use the following:
```
df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
```
We will then need to rebuild our Docker image before ingesting the data.

Now that we have the `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns in the date format, we can simply count the number of rows that have the `2019-01-15` date in both columns.
```
SELECT
	TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') AS pickup_date,
	TO_CHAR(lpep_dropoff_datetime, 'YYYY-MM-DD') AS dropoff_date,
	COUNT(*)
FROM green_taxi_trips
GROUP BY pickup_date, dropoff_date
HAVING
	TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') = '2019-01-15' AND
	TO_CHAR(lpep_dropoff_datetime, 'YYYY-MM-DD') = '2019-01-15';
```
Which outputs:
```
pickup_date | dropoff_date | count
----------------------------------
2019-01-15  | 2019-01-15   | 20530
```


## Question 4. Largest trip for each day
> Which was the day with the largest trip distance? Use the pick up time for your calculations.
> 
> - 2019-01-18
> - 2019-01-28
> - 2019-01-15
> - 2019-01-10

To find the day with the largest trip distance, we will select the largest trip distance for each day, order by the largest trip first, and then limit the output to return only the first row:
```
SELECT
	TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') AS pickup_date,
	MAX(trip_distance) AS largest_trip_distance
FROM green_taxi_trips
GROUP BY pickup_date 
ORDER BY largest_trip_distance DESC
LIMIT 1;
```
Which outputs:
```
pickup_date | largest_trip_distance
-----------------------------------
2019-01-15  | 117.99
```


## Question 5. The number of passengers
> In 2019-01-01 how many trips had 2 and 3 passengers?
> 
> - 2: 1282 ; 3: 266
> - 2: 1532 ; 3: 126
> - 2: 1282 ; 3: 254
> - 2: 1282 ; 3: 274

We can create 2 sub-select statments, one to select the number of 2 passenger rides on 2019-01-01, and another to select the number of 3 passenger rides on 2019-01-01, and return these within the same table.
```
SELECT
	TO_CHAR(
		lpep_pickup_datetime, 'YYYY-MM-DD'
	) AS pickup_date,
	(
		SELECT COUNT(*)
		FROM green_taxi_trips
		WHERE passenger_count = 2 AND
		TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') = '2019-01-01'
	) AS num_of_2_passengers,
	(
		SELECT COUNT(*)
		FROM green_taxi_trips
		WHERE passenger_count = 3 AND
		TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') = '2019-01-01'
	) AS num_of_3_passengers
FROM green_taxi_trips
GROUP BY pickup_date
HAVING TO_CHAR(lpep_pickup_datetime, 'YYYY-MM-DD') = '2019-01-01';
```
Which outputs:
```
pickup_date | num_of_2_passengers | num_of_3_passengers
-------------------------------------------------------
2019-01-01  | 1282                | 254
```


## Question 6. Largest tip
> For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? We want the name of the zone, not the id.
> 
> Note: it's not a typo, it's tip , not trip
> 
> - Central Park
> - Jamaica
> - South Ozone Park
> - Long Island City/Queens Plaza

We could perform 2 `INNER JOIN` statements on the `zone_lookup` table so that we can select and compare the pickup location against the dropoff location. 

Using the `HAVING` clause will allow us to select only the `Astoria` pickup location while still obtaining all associaded trip dropoff locations.
```
SELECT 
	MAX(tip_amount) AS max_tip_amount,
	pu_loc.zone AS pickup_zone,
	do_loc.zone AS dropoff_zone
FROM green_taxi_trips
INNER JOIN zone_lookup AS pu_loc ON
pulocationid = pu_loc.locationid 
INNER JOIN zone_lookup AS do_loc ON
dolocationid = do_loc.locationid
GROUP BY pickup_zone, dropoff_zone
HAVING pu_loc.zone = 'Astoria'
ORDER BY MAX(tip_amount) DESC
LIMIT 1;
```
Which outputs:
```
max_tip_amount | pickup_zone | dropoff_zone
------------------------------------------------------------
88             | Astoria     | Long Island City/Queens Plaza
```
