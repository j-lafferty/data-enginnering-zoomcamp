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

