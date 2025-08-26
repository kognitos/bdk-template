import subprocess
import os
import argparse
import sys

from dotenv import load_dotenv
load_dotenv()

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, env=os.environ.copy()).returncode

def run_tests():
    # generate coverage report
    return run_cmd("poetry run pytest -vv --junit-xml=test-results.xml")

def run_test():
    # Run a single test, supporting snapshot updates and cassette re-writing
    parser = argparse.ArgumentParser(
        description="Run a single test, supporting snapshot updates and cassette re-writing."
    )
    parser.add_argument(
        "-k",
        metavar="<expression>",
        help="(required) run tests matching the given expression."
    )
    parser.add_argument(
        "-u", "--update",
        action="store_true",
        help="update snapshots (adds --snapshot-update)"
    )
    parser.add_argument(
        "-r", "--record",
        action="store_true",
        help="re-record cassettes (adds --record-mode=rewrite)"
    )

    args = parser.parse_args()

    # Require -k
    if not args.k:
        parser.print_help()
        sys.exit(1)

    # Build pytest command string
    cmd = f"{sys.executable} -m pytest -k '{args.k}'"

    if args.update:
        cmd += " --snapshot-update"

    if args.record:
        cmd += " --record-mode=rewrite"

    sys.exit(run_cmd(cmd))

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
    if not (ngrok_token := os.getenv("NGROK_AUTHTOKEN")):
        raise ValueError("Missing NGROK api key")
    cmd = f"docker run --rm -e BDK_SERVER_MODE=book -e BDK_TRANSPORT_MODE=ngrok -e NGROK_AUTHTOKEN={ngrok_token}"
    if ngrok_domain := os.getenv("BDK_NGROK_DOMAIN"):
        cmd += f" -e BDK_NGROK_DOMAIN={ngrok_domain}"
    cmd += f" {image_tag}"
    run_cmd(cmd)
