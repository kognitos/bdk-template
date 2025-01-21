<img src="src/{{ cookiecutter.project_slug }}/data/icon.svg" width="128" height="128">

# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Prerequisites
Before you begin, ensure you have the following installed on your system:

### Python 3.11
The project is developed with Python 3.11. You can use [pyenv](https://github.com/pyenv/pyenv), [homebrew](https://formulae.brew.sh/formula/python@3.11), [apt](https://linuxcapable.com/how-to-install-python-3-11-on-ubuntu-linux/), or [manual installation](https://www.python.org/downloads/).
 
### Poetry
Poetry is used for dependency management and packaging in this project. You can find the installation guide [here](https://python-poetry.org/docs/).

### Configure Poetry
Once poetry is installed, [configure poetry](https://python-poetry.org/docs/configuration/#virtualenvsin-project) to create the virtual environment inside the project’s root directory, by running this:

```Text CLI
poetry config virtualenvs.in-project true
```

## Setting Up the Project

### Clone the Repository
Ensure you have the necessary permissions to access the repository and clone it to your local machine:

```shell
git clone <book repository>
cd <book project>
```

### Install Dependencies
Use Poetry to install all required dependencies in an isolated environment.

```shell
poetry env use 3.11
poetry install
```

### Activate the virtual environment

There are many ways of doing this, depending on your poetry version.

- Running `poetry shell`

or

- Manually activating the venv:
  ```
  source <path_to_your_venv>/bin/activate
  ```
    If the venv was created locally in-project, run `source .venv/bin/activate`. Otherwise, look at where the env was created when you ran `poetry env use 3.11`.

## Running Tests
This book uses Pytest as its test runner. You can execute it using the following command:

```shell
poetry run tests
```

## Formatting Code
This book uses black and isort as its source formatter. You can execute it using the following command:

```shell
poetry run format
```

## Linting Code
This book uses pylint as its source linter. You can execute it using the following command:

```shell
poetry run lint
```

## Generate usage documentation
This script automatically generates a comprehensive USAGE.md file from the docstrings:

```shell
poetry run doc
```

## Running locally for testing (using docker and ngrok)
You can run the image locally, and use ngrok to make your image routable from the playground:

- You need to install [docker](https://www.docker.com) if you haven't already.
- You need to install and configure [ngrok](https://ngrok.com/) (you need an account, and you have to set up an API KEY. The free tier is enough).

After that, you need to configure ngrok api key as an environment variable:

```shell
export NGROK_AUTHTOKEN=<YOUR_API_KEY>
```

Finally, run the poetry script to host the book locally:

```shell
poetry run host
```

When you run this, you are going to see some logs. One of which contains the ngrok address: `listening on https://<SOME_UUID>.ngrok-free.app`. You need to copy this url and paste it on your kognitos playground using the learn command like this:

```
learn "https://5aad-186-127-136-101.ngrok-free.app"
```

## Building Docker image
In order to deploy the book, a docker image must be build that wraps the book with the BDK runtime:

```shell
docker build -t {{ cookiecutter.project_slug }}:<VERSION> .
```

## Deploying the Docker image
Once the image is built and tested, you can deploy it anywhere plublicly routable (remember to bind the correct port in the Dockerfile to the port your infrastructure exposes). After that you can learn from that endpoint in the Kognitos playground like this:

```
learn "<HOST_URI_HERE>"
```
