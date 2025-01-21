import subprocess
import os

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, env=os.environ.copy()).returncode

def run_tests():
    # generate coverage report
    return run_cmd("poetry run pytest -vv --junit-xml=test-results.xml")

def run_format():
    # format all files in-place
    return run_cmd("poetry run black src tests")
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
    runtime_version = toml.load('pyproject.toml')['environment'].get('bdk_runtime_version', 'latest')
    bdk_runtime_uri = f"kognitosinc/bdk:{runtime_version}"
    image_tag = "{{ cookiecutter.project_slug }}:local_test"
    run_cmd(f"docker build --build-arg BDK_RUNTIME_IMAGE_URI={bdk_runtime_uri} -t {image_tag} .")
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if not ngrok_token:
        raise ValueError("Missing NGROK api key")
    run_cmd(f"docker run --rm -e BDK_SERVER_MODE=ngrok -e NGROK_AUTHTOKEN={ngrok_token} {image_tag}")