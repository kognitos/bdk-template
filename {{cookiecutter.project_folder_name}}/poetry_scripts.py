import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import docker
import toml
from docker.errors import APIError, NotFound
from docker.models.volumes import Volume
from dotenv import load_dotenv

load_dotenv()

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, env=os.environ.copy()).returncode

def run_tests():
    # Generate coverage report
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
    # Format all files in-place
    run_cmd("poetry run black src tests")
    # Organize imports
    return run_cmd("poetry run isort src tests")

def run_lint():
    # Lint source and test files
    return run_cmd("poetry run pylint --output-format=colorized src tests")

def run_type_check():
    # Type check source
    return run_cmd("poetry run pyright")

def run_doc():
    # Generate documentation
    return run_cmd("poetry bdk usage")


def run_host():
    # Run host using a runtime image and using cached dependencies
    runtime_version = _get_runtime_version()
    bdk_runtime_image = f"kognitosinc/bdk:{runtime_version}"
    ngrok_token, ngrok_domain = _get_ngrok_credentials()
    volume_name = _get_volume_name()
    success, initialized_volume = _initialize_dependencies_volume(
        bdk_runtime_image, volume_name
    )
    if not success:
        print("Failed to initialize dependencies volume")
        return 1
    return _run_host_container(
        bdk_runtime_image, ngrok_token, ngrok_domain, initialized_volume
    )

def run_clean_host_cache():
    # Cleans cache created for host
    client = _get_docker_client()
    volumes = _list_dependency_volumes()
    if not volumes:
        print("No dependency volumes found")
    else:
        _clean_volumes_and_containers(client, volumes)
    _clean_build_cache(client)
    print("\nHost cache and volumes cleaned successfully")
    return 0


def run_build_host():
    # Run build host which builds book image and runs it
    runtime_version = _get_runtime_version()
    bdk_runtime_image = f"kognitosinc/bdk:{runtime_version}"
    project_name = _get_project_name()
    image_tag = f"{project_name}:local_test"
    ngrok_token, ngrok_domain = _get_ngrok_credentials()
    if not _build_docker_image(bdk_runtime_image, image_tag):
        return 1
    return _run_docker_image(image_tag, ngrok_token, ngrok_domain)


def run_check_all():
    # Run all checks, if any check fails (returns non-zero), immediately return that error code
    result = run_format()
    if result != 0:
        return result

    result = run_lint()
    if result != 0:
        return result

    result = run_type_check()
    if result != 0:
        return result

    result = run_tests()
    if result != 0:
        return result

    # All checks passed
    return 0


def _get_runtime_version(pyproject_path: str = "pyproject.toml") -> str:
    return (
        toml.load(pyproject_path)
        .get("environment", {})
        .get("bdk_runtime_version", "latest")
    )


def _get_ngrok_credentials() -> tuple[str, Optional[str]]:
    token = os.getenv("NGROK_AUTHTOKEN")
    if not token:
        raise ValueError("Missing NGROK api key")
    return token, os.getenv("NGROK_DOMAIN")


def _get_project_root() -> Path:
    return Path(__file__).parent.absolute()


def _get_dependencies_hash() -> str:
    project_root = _get_project_root()
    lock_file = project_root / "poetry.lock"

    if not lock_file.exists():
        raise FileNotFoundError(
            "poetry.lock not found. Run 'poetry lock' to generate it."
        )

    content = lock_file.read_bytes()
    return hashlib.sha256(content).hexdigest()


def _get_project_name() -> str:
    project_root = _get_project_root()
    pyproject_file = project_root / "pyproject.toml"
    if pyproject_file.exists():
        data = toml.load(pyproject_file)
        return data.get("tool", {}).get("poetry", {}).get("name", "book")
    return "book"


def _get_volume_name() -> str:
    project_name = _get_project_name()
    deps_hash = _get_dependencies_hash()
    return f"{project_name}-deps-{deps_hash}"


def _get_docker_client() -> docker.DockerClient:
    return docker.from_env()


def _check_volume_exists(volume_name: str) -> bool:
    client = _get_docker_client()
    try:
        client.volumes.get(volume_name)
        return True
    except NotFound:
        return False


def _create_volume(volume_name: str) -> Volume:
    client = _get_docker_client()
    return client.volumes.create(name=volume_name)


def _initialize_dependencies_volume(
    bdk_runtime_image: str, volume_name: str
) -> Tuple[bool, str]:
    if _check_volume_exists(volume_name):
        return True, volume_name

    print(f"Creating and initializing dependencies volume: {volume_name}")
    _create_volume(volume_name)

    client = _get_docker_client()
    project_root = _get_project_root()

    install_commands = [
        "set -e",
        "python3 -m venv /opt/deps/venv",
        "/opt/deps/venv/bin/pip install --upgrade pip setuptools wheel",
        "/opt/deps/venv/bin/pip install poetry",
        "export POETRY_VIRTUALENVS_CREATE=false",
        "export POETRY_VIRTUALENVS_IN_PROJECT=false",
        "source /opt/deps/venv/bin/activate",
        "cd /tmp/project",
        "poetry install --only main",
        "PYVER=$(python3 -c 'import sys; print(f\"python{sys.version_info.major}.{sys.version_info.minor}\")')",
        "SP=/opt/deps/venv/lib/$PYVER/site-packages",
        "ln -sfn \"$SP\" /opt/deps/site-packages",
        "sed -i 's|/tmp/project|/book|g' \"$SP\"/*.egg-link 2>/dev/null || true",
        "sed -i 's|/tmp/project|/book|g' \"$SP\"/*.pth 2>/dev/null || true",
        "sed -i 's|/tmp/project|/book|g' \"$SP\"/easy-install.pth 2>/dev/null || true",
        "echo 'Dependencies installed successfully'",
    ]

    install_script = " && ".join(install_commands)

    try:
        print(f"Installing dependencies in volume {volume_name}...")
        container = client.containers.run(
            bdk_runtime_image,
            command=["-c", install_script],
            volumes={
                volume_name: {"bind": "/opt/deps", "mode": "rw"},
                str(project_root): {"bind": "/tmp/project", "mode": "ro"},
            },
            working_dir="/tmp",
            entrypoint="/bin/sh",
            remove=True,
            detach=False,
            stdout=True,
            stderr=True,
        )
        output = container.decode() if isinstance(container, bytes) else str(container)
        print(output)
        return True, volume_name
    except Exception as e:
        print(f"Failed to initialize volume: {e}")
        try:
            client.volumes.get(volume_name).remove()
        except Exception:
            pass
        return False, ""


def _list_dependency_volumes() -> list[Volume]:
    client = _get_docker_client()
    project_name = _get_project_name()
    return [
        v for v in client.volumes.list() if v.name.startswith(f"{project_name}-deps")
    ]


def _build_docker_image(bdk_runtime_uri: str, image_tag: str) -> bool:
    client = _get_docker_client()
    project_root = _get_project_root()

    try:
        print(f"Building Docker image {image_tag}...")
        _, build_logs = client.images.build(
            path=str(project_root),
            tag=image_tag,
            buildargs={
                "BDK_RUNTIME_IMAGE_URI": bdk_runtime_uri,
            },
            rm=True,
        )
        for log in build_logs:
            print(log)
        return True
    except Exception as e:
        print(f"Build failed: {e}")
        return False


def _run_docker_image(
    image_tag: str, ngrok_token: str, ngrok_domain: Optional[str]
) -> int:
    client = _get_docker_client()

    environment = {
        "BDK_SERVER_MODE": "book",
        "BDK_TRANSPORT_MODE": "ngrok",
        "NGROK_AUTHTOKEN": ngrok_token,
        "OTEL_SDK_DISABLED": "true",
    }

    if ngrok_domain:
        environment["BDK_NGROK_DOMAIN"] = ngrok_domain
    else:
        print("NGROK domain not provided, defaulting")

    try:
        client.containers.run(
            image_tag,
            entrypoint="/var/runtime/bootstrap",
            environment=environment,
            remove=True,
            detach=False,
            stdin_open=False,
            tty=False,
        )
        return 0
    except Exception as e:
        print(f"Container failed: {e}")
        return 1


def _run_host_container(
    bdk_runtime_image: str,
    ngrok_token: str,
    ngrok_domain: Optional[str],
    volume_name: str,
) -> int:
    client = _get_docker_client()
    project_root = _get_project_root()
    deps_path = "/opt/deps/site-packages"

    environment = {
        "BDK_SERVER_MODE": "book",
        "BDK_TRANSPORT_MODE": "ngrok",
        "NGROK_AUTHTOKEN": ngrok_token,
        "OTEL_SDK_DISABLED": "true",
        "BDK_RUNTIME_PYTHON_BOOK_PATH": deps_path,
        "PYTHONPATH": f"/book/src:{deps_path}",
        "PATH": "/opt/deps/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    }

    if ngrok_domain:
        environment["BDK_NGROK_DOMAIN"] = ngrok_domain
    else:
        print("NGROK domain not provided, defaulting")

    try:
        container = client.containers.run(
            bdk_runtime_image,
            entrypoint="/var/runtime/bootstrap",
            volumes={
                volume_name: {"bind": "/opt/deps", "mode": "ro"},
                str(project_root / "src"): {"bind": "/book/src", "mode": "ro"},
            },
            environment=environment,
            remove=False,
            detach=True,
        )

        try:
            for line in container.logs(stream=True, follow=True):
                print(line.decode("utf-8").rstrip())
        except KeyboardInterrupt:
            print("\nKilling container...")
            container.kill()
            container.remove()
            return 0

        container.wait()
        exit_code = container.attrs["State"]["ExitCode"]
        container.remove()
        return exit_code

    except Exception as e:
        print(f"Container failed: {e}")
        return 1


def _find_containers_using_volumes(client, volume_names):
    """Find all containers using specified volumes."""
    print("Checking for containers using these volumes...")
    containers_to_stop = []

    for container in client.containers.list(all=True):
        mounts = container.attrs.get("Mounts", [])
        if any(mount.get("Name") in volume_names for mount in mounts):
            containers_to_stop.append(container)

    return containers_to_stop


def _stop_and_remove_containers(containers):
    """Stop and remove containers gracefully."""
    print(f"Stopping and removing {len(containers)} container(s) using volumes...")

    for container in containers:
        container_id = container.name or container.id[:12]

        if not _stop_container(container, container_id):
            _force_kill_container(container, container_id)

        _remove_container(container, container_id)


def _stop_container(container, container_id, timeout=5):
    """Attempt to gracefully stop a container."""
    try:
        print(f"\tStopping container: {container_id}")
        container.stop(timeout=timeout)
        return True
    except Exception:
        return False


def _force_kill_container(container, container_id):
    """Force kill a container if graceful stop failed."""
    try:
        print(f"\tForce killing container: {container_id}")
        container.kill()
    except Exception:
        pass


def _remove_container(container, container_id):
    """Remove a container."""
    try:
        print(f"\tRemoving container: {container_id}")
        container.remove(force=True, v=True)
    except APIError as e:
        print(f"\tError removing container: {e}")


def _remove_volumes(volumes):
    """Remove Docker volumes."""
    print("Removing dependency volumes...")

    for volume in volumes:
        print(f"\tRemoving volume: {volume.name}")
        try:
            volume.remove(force=True)
            print(f"\t\tVolume {volume.name} removed successfully")
        except APIError as e:
            print(f"\t\tError removing {volume.name}: {e}")


def _clean_build_cache(client):
    """Clean Docker build cache."""
    print("\nCleaning Docker build cache...")
    try:
        prune_result = client.api.prune_builds()
        space_reclaimed = prune_result.get("SpaceReclaimed", 0)

        if space_reclaimed > 0:
            print("\tBuild cache cleaned")
        else:
            print("\tNo build cache to clean")
    except APIError as e:
        print(f"\tError cleaning build cache: {e}")


def _clean_volumes_and_containers(client, volumes):
    """Clean Docker volumes and their associated containers."""
    volume_names = {v.name for v in volumes}
    print(f"Found {len(volumes)} dependency volume(s)")

    containers = _find_containers_using_volumes(client, volume_names)
    if containers:
        _stop_and_remove_containers(containers)

    _remove_volumes(volumes)


