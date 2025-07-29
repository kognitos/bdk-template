import subprocess
import os

from dotenv import load_dotenv
load_dotenv()

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, env=os.environ.copy()).returncode

def run_tests():
    # generate coverage report
    return run_cmd("poetry run pytest -vv --junit-xml=test-results.xml")

def run_format():
    # format all files in-place
    run_cmd("poetry run black src tests")
    # organize imports
    return run_cmd("poetry run isort src tests")

def run_lint():
    # lint source and test files
    return run_cmd("poetry run pylint --output-format=colorized src tests")

def run_type_check():
    # type check source
    return run_cmd("poetry run pyright")

def run_doc():
    # generate documentation
    return run_cmd("poetry bdk usage")

def run_host():
    # build and run docker image
    image_tag = "{{ cookiecutter.project_slug }}:local_test"
    run_cmd(f"docker build -t {image_tag} .")
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if not ngrok_token:
        raise ValueError("Missing NGROK api key")
    run_cmd(f"docker run --rm -e BDK_SERVER_MODE=book -e BDK_TRANSPORT_MODE=ngrok -e NGROK_AUTHTOKEN={ngrok_token} {image_tag}")