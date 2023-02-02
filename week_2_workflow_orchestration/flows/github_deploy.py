from prefect.deployments import Deployment
from prefect.filesystems import GitHub
from parameterized_flow import etl_parent_flow


github_block = GitHub.load("zoom-gcs")

github_sb = github_block.get_directory(  # (from_path, to_path--default=pwd)
    "week_2_workflow_orchestration/flows", "github_sb"
)

github_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name="github_deploy",
    storage=github_sb,
    parameters={"months": [11], "year": 2020, "color": "green"},
)


if __name__ == "__main__":
    github_dep.apply()
