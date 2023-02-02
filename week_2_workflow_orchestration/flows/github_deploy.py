from prefect.filesystems import GitHub


github_block = GitHub.load("zoom-gcs")

github_block.get_directory(  # (from_path, to_path--default=pwd)
    "week_2_workflow_orchestration/flows", "github_sb"
)


if __name__ == "__main__":
    github_block.save("github_sb")
