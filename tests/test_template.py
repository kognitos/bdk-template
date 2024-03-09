import os
import tomllib

import pytest
from generate_project import generate_project

PROJECT_SLUG = "test_project"
PROJECT_NAME = "Test Project"
PROJECT_CLASS = "TestProject"


@pytest.mark.parametrize(
    "generate_project",
    [{"project_slug": PROJECT_SLUG, "project_name": PROJECT_NAME}],
    indirect=True,
)
def test_pyproject(generate_project):
    project_path = generate_project
    pyproject_path = os.path.join(project_path, "pyproject.toml")

    with open(pyproject_path, "rb") as f:
        pyproject_content = tomllib.load(f)

    # Verify the project name in the pyproject.toml
    actual_project_name = pyproject_content["tool"]["poetry"]["name"]
    assert actual_project_name == PROJECT_SLUG

    # Verify entry point
    entry_point = (
        pyproject_content.get("tool", {})
        .get("poetry", {})
        .get("plugins", {})
        .get("kognitos-book", {})
        .get(PROJECT_SLUG, None)
    )
    assert entry_point == f"{PROJECT_SLUG}.book:{PROJECT_CLASS}"
