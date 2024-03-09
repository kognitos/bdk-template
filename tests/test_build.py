import glob
import os
import subprocess

import pytest
from change_dir import change_dir
from generate_project import generate_project

PROJECT_SLUG = "test_project"
PROJECT_NAME = "Test Project"


@pytest.mark.parametrize(
    "generate_project",
    [{"project_slug": PROJECT_SLUG, "project_name": PROJECT_NAME}],
    indirect=True,
)
def test_build(generate_project):
    project_path = generate_project

    with change_dir(project_path):
        # run `poetry build` to build the project
        result = subprocess.run(["poetry", "build"], capture_output=True, text=True)

        # check if build was successful (exit code 0 means success)
        assert (
            result.returncode == 0
        ), f"Poetry build failed with error: {result.stderr}"

        # find the generated wheel file
        wheel_files = glob.glob("dist/*.whl")
        assert len(wheel_files) > 0, "No wheel file found in the dist directory."

        # use twine to check the wheel file for common issues
        check_result = subprocess.run(
            ["twine", "check", wheel_files[0]], capture_output=True, text=True
        )

        # check if twine check was successful
        assert (
            check_result.returncode == 0
        ), f"Twine check failed with error: {check_result.stderr}"
