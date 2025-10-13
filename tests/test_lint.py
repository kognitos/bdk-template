import os
import subprocess

import pytest
from change_dir import change_dir
from generate_project import generate_project
from pylint.lint import Run
from pylint.reporters import CollectingReporter

PROJECT_SLUG = "test_project"
PROJECT_NAME = "Test Project"


def run_pylint(project_directory):
    report = CollectingReporter()

    src_directory = os.path.join(project_directory, "src", PROJECT_SLUG)

    with change_dir(project_directory):
        result = subprocess.run(["poetry", "install"], capture_output=True, text=True)

        try:
            pylint_output = Run([src_directory], reporter=report, exit=False)

            pylint_score = pylint_output.linter.stats.global_note
        except Exception as e:
            pylint_score = None

    return pylint_score, report.messages


@pytest.mark.parametrize(
    "generate_project",
    [{"project_slug": PROJECT_SLUG, "project_name": PROJECT_NAME}],
    indirect=True,
)
def test_pylint_passes(generate_project):
    pylint_score, pylint_messages = run_pylint(generate_project)

    # Check if pylint passed
    assert (
        pylint_score == 10.0
    ), f"Pylint failed with score {pylint_score}\n{pylint_messages}"
