
import subprocess
import pytest

from change_dir import change_dir
from generate_project import generate_project


PROJECT_SLUG = "test_project"
PROJECT_NAME = "Test Project"


def run_tests(project_directory):
    with change_dir(project_directory):
        install_result = subprocess.run(["poetry", "install"], capture_output=True, text=True)
        tests_result = subprocess.run(["poetry", "run", "tests"], capture_output=True, text=True)

    return install_result, tests_result


@pytest.mark.parametrize(
    "generate_project",
    [{"project_slug": PROJECT_SLUG, "project_name": PROJECT_NAME}],
    indirect=True,
)
def test_run_tests_passes(generate_project):
    install_result, tests_result = run_tests(generate_project)

    assert install_result.returncode == 0, "'poetry install' command failed in generated book"
    assert tests_result.returncode == 0, f"'poetry run tests' command failed in generated book. Output: \n\n{tests_result.stdout}"

