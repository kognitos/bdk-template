# Book Template

This Cookiecutter template sets up a basic Python project structure, aiming to save you time and 
to promote best practices. It's ideal for starting new Book projects quickly with a standard 
setup including a project structure, basic documentation, and necessary configuration files.

## Features

- Basic project structure with a dedicated source directory
- `README.md` template
- Adheres to PEP 518 with a configured `pyproject.toml`
- `.gitignore` file configured for Python projects
- Sample tests setup with `pytest`
- Poetry for managing dependencies

## Requirements

Before you can use this template, you'll need to install Cookiecutter. You can install it 
via pip:

```bash
pip install cookiecutter
```

## Usage

To generate a new project using this template, run:

```bash
cookiecutter  git+ssh://git@github.com/kognitos/bdk-template.git
```

You will be prompted to enter values for various configuration options (e.g., project name, 
author name). Default values are provided for each option, which you can accept by pressing 
Enter, or you can provide your own.

## Configuration Options

The following options are available when generating a project from this template:

* *project_name*: The name of your project (default: "My Python Project").
* *project_slug*: A URL-friendly version of the project name, usually derived automatically from the project name.
* *project_description*: A short description of your project.
* *author_name*: Your (or your organization's) name.
* *initial_version*: Initial project version.
