<img src="src/{{ cookiecutter.project_slug }}/data/icon.svg" width="128" height="128">

# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Prerequisites
Before you begin, ensure you have the following installed on your system:

### Python 3.11
The project is developed with Python 3.11. We recommend using Pyenv to manage your Python versions.

To manage Python 3.11 with Pyenv, follow these steps:

#### Install Pyenv
If you haven't installed Pyenv yet, you can find the installation instructions on the Pyenv GitHub page. The 
installation process varies depending on your operating system.

#### Install Python 3.11
Once Pyenv is installed, you can install Python 3.11 using the following command:

```shell
pyenv install 3.11
```
 
### Poetry
Poetry is used for dependency management and packaging in this project. 

#### Install Poetry
Run the following command to install Poetry:

```shell
curl -sSL https://install.python-poetry.org | python3 -
```
#### [Configure Poetry](https://python-poetry.org/docs/configuration/#virtualenvsin-project) to create the virtual environment inside the project’s root directory:

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
poetry shell
poetry install
```

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

## Building Docker image using BDK Runtime
In order to deploy the book, a docker image must be build that wraps the book with the BDK runtime:

```shell
docker build -t {{ cookiecutter.project_slug }}:<VERSION> .
```

## Running Docker image locally for testing (using ngrok)
You can run the image locally, and use ngrok to make your image routable from the playground:

- You need to install [ngrok](https://ngrok.com/) locally.
- You need an [ngrok](https://ngrok.com/) account, and you have to set up an API KEY (The free tier is enough).

After that, you just need to run the docker image using the ngrok mode:

```shell
docker run -e BDK_SERVER_MODE=ngrok -e NGROK_AUTHTOKEN=<YOUR_API_KEY> {{ cookiecutter.project_slug }}:<VERSION>
```

When you run this, you are going to see some logs. One of which contains the ngrok address: `listening on https://<SOME_UUID>.ngrok-free.app`. You need to copy this url and paste it on your kognitos playground using the learn command like this:

```
learn "https://5aad-186-127-136-101.ngrok-free.app"
```

## Deploying the Docker image
Once the image is built and tested, you can deploy it anywhere plublicly routable (remember to bind the correct port in the Dockerfile to the port your infrastructure exposes). After that you can learn from that endpoint in the Kognitos playground like this:

```
learn "<HOST_URI_HERE>"
```
