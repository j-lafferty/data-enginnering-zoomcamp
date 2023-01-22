# Data Engineering ZoomCamp - Week 1 Homework
[Week 1 Homework](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2023/week_1_docker_sql/homework.md)


## Question 1. Knowing docker tags
> Which tag has the following text? - Write the image ID to the file
>
> - --imageid string
> - --iidfile string
> - --idimage string
> - --idfile string

We're looking for a tag that has to deal with command that writes images.

By typing 'docker --help' we will find one docker command that does this:
'''
build       Build an image from a Dockerfile
'''

We can now lookup the differnt tags associated with 'docker build' by typing 'docker build --help'. Doing so, we will find that the answer to this question is:
'''
--iidfile string          Write the image ID to the file
'''