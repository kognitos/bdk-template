import os

import pytest
from cookiecutter.main import cookiecutter


@pytest.fixture
def generate_project(request, tmpdir):
    """
    Generate a project using Cookiecutter.

    :param tmpdir: The temporary directory for generating the project.
    :return: The path to the generated project directory.
    """
    # Get the current working directory of the test file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Assuming your Cookiecutter template is in the root of your project directory,
    # and your tests are in a subdirectory, adjust the path as necessary
    template_path = os.path.join(
        current_dir,
        "..",
    )

    # Create output directory
    output_dir = str(tmpdir.mkdir("output"))

    cookiecutter(
        template_path,
        no_input=True,
        extra_context=request.param,
        output_dir=output_dir,
    )
    return os.path.join(
        output_dir, "book-" + request.param["project_slug"].replace("_", "-")
    )
