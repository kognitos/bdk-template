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