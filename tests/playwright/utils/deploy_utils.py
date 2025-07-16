from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import warnings
from typing import Any, Callable, List, Optional, TypeVar

import pytest
import requests
from conftest import ScopeName

from shiny.run._run import shiny_app_gen

is_interactive = hasattr(sys, "ps1")
reruns = 1 if is_interactive else 3
reruns_delay = 1

LOCAL_LOCATION = "local"

__all__ = (
    "local_deploys_app_url_fixture",
    "skip_if_not_chrome",
)

# connect
server_url = os.environ.get("DEPLOY_CONNECT_SERVER_URL")
api_key = os.environ.get("DEPLOY_CONNECT_SERVER_API_KEY")
# shinyapps.io
shinyappsio_name = os.environ.get("DEPLOY_SHINYAPPS_NAME")
shinyappsio_token = os.environ.get("DEPLOY_SHINYAPPS_TOKEN")
shinyappsio_secret = os.environ.get("DEPLOY_SHINYAPPS_SECRET")

run_on_ci = os.environ.get("CI", "False") == "true"
repo = os.environ.get("GITHUB_REPOSITORY", "unknown")

should_use_github_requirements_txt = (
    os.environ.get("DEPLOY_GITHUB_REQUIREMENTS_TXT", "true").lower() == "true"
)


deploy_locations: List[str] = ["connect", "shinyapps"]


CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def skip_if_not_chrome(fn: CallableT) -> CallableT:
    # # Keeping commented to allow for easier local debugging
    # import platform
    # fn = pytest.mark.skipif(
    #     platform.python_version_tuple()[:2] != ("3", "10"),
    #     reason="Test requires Python 3.10",
    # )(fn)
    fn = pytest.mark.only_browser("chromium")(fn)

    return fn


def skip_on_webkit(fn: CallableT) -> CallableT:
    fn = pytest.mark.skip_browser("webkit")(fn)

    return fn


def skip_on_python_version(
    version: str,
    reason: Optional[str] = None,
) -> Callable[[CallableT], CallableT]:

    reason_str = reason or f"Do not run on python {version}"

    is_valid_version = (
        re.match(r"\d+", version)
        or re.match(r"\d+\.\d+", version)
        or re.match(r"\d+\.\d+\.\d+", version)
    ) is not None

    assert is_valid_version

    def _(fn: CallableT) -> CallableT:

        versions_match = True
        for i, v in enumerate(version.split(".")):
            if sys.version_info[i] != int(v):
                versions_match = False
                break

        fn = pytest.mark.skipif(
            versions_match,
            reason=reason_str,
        )(fn)

        return fn

    return _


def run_command(cmd: str) -> str:
    output = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        shell=True,
    )
    if output.returncode != 0:
        print(
            "Failed to run command!",
            "\nstdout:",
            output.stdout,
            "\nstderr:",
            output.stderr,
            file=sys.stderr,
            sep="\n",
        )
        raise RuntimeError(f"Failed to run command: {redact_api_key(cmd)}")
    return output.stdout


def redact_api_key(cmd: str) -> str:
    # Redact the value of the `--api-key` CLI argument, replace it with `***`
    # Create a regex that replaces the argument following `--api-key`
    # with `***` (e.g. `--api-key my-api-key` -> `--api-key ***`)

    return re.sub(r"(--api-key\s+)(\S+)", r"\1***", cmd)


def deploy_to_connect(app_name: str, app_dir: str) -> str:
    if not api_key:
        raise RuntimeError("No api key found. Cannot deploy.")

    # check if connect app is already deployed to avoid duplicates
    connect_server_lookup_command = f"rsconnect content search --server {server_url} --api-key {api_key} --title-contains {app_name}"
    app_details = run_command(connect_server_lookup_command)
    connect_server_deploy = f"rsconnect deploy shiny {app_dir} --server {server_url} --api-key {api_key} --title {app_name} --verbose"
    # only if the app exists do we replace existing app with new version
    if json.loads(app_details):
        app_id = json.loads(app_details)[0]["guid"]
        connect_server_deploy += f" --app-id {app_id}"

    # Deploy to connect server
    run_command(connect_server_deploy)

    # look up content url in connect server once app is deployed
    output = run_command(connect_server_lookup_command)
    url = json.loads(output)[0]["content_url"]
    app_id = json.loads(output)[0]["guid"]

    # change visibility of app to public
    connect_app_url = f"{server_url}/__api__/v1/content/{app_id}"
    payload = '{"access_type":"all"}'
    headers = {
        "Authorization": f"Key {api_key}",
        "Accept": "application/json",
    }
    response = requests.request("PATCH", connect_app_url, headers=headers, data=payload)
    if response.status_code != 200:
        warnings.warn(
            f"Failed to change visibility of app. {response.text}",
            RuntimeWarning,
            stacklevel=1,
        )
        pytest.skip(
            "Skipping test as deployed app is not visible to public. Test is kept as it does confirm the app deployment has succeeded."
        )
        return

    return url


# TODO-future: Supress web browser from opening after deploying - https://github.com/rstudio/rsconnect-python/issues/462
def deploy_to_shinyapps(app_name: str, app_dir: str) -> str:
    # Deploy to shinyapps.io
    shinyapps_deploy = f"rsconnect deploy shiny {app_dir} --account {shinyappsio_name} --token {shinyappsio_token} --secret {shinyappsio_secret} --title {app_name} --verbose"
    run_command(shinyapps_deploy)
    return f"https://{shinyappsio_name}.shinyapps.io/{app_name}/"


# Since connect parses python packages, we need to get latest version of shiny on HEAD
def write_github_requirements_txt(app_dir: str) -> None:
    print("Writing github requirements.txt")
    app_requirements_file_path = os.path.join(app_dir, "app_requirements.txt")
    requirements_file_path = os.path.join(app_dir, "requirements.txt")
    git_cmd = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    git_hash = git_cmd.stdout.decode("utf-8").strip()
    with open(app_requirements_file_path) as f:
        requirements = f.read()
    with open(requirements_file_path, "w") as f:
        f.write(f"{requirements}\n")
        f.write(f"git+https://github.com/posit-dev/py-shiny.git@{git_hash}\n")


def write_pypi_requirements_txt(app_dir: str) -> None:
    print("Writing pypi requirements.txt")
    app_requirements_file_path = os.path.join(app_dir, "app_requirements.txt")
    requirements_file_path = os.path.join(app_dir, "requirements.txt")

    with open(app_requirements_file_path) as f:
        requirements = f.read()
    with open(requirements_file_path, "w") as f:
        f.write(f"{requirements}\n")
        f.write("shiny\n")


def assert_rsconnect_file_updated(file_path: str, min_mtime: float) -> None:
    """
    Asserts that the specified file has been updated since `min_mtime` (seconds since epoch).
    """
    mtime = os.path.getmtime(file_path)
    assert (
        mtime > min_mtime
    ), f"File '{file_path}' was not updated during app deployment which means the deployment failed"


def deploy_app(
    app_file_path: str,
    location: str,
    app_name: str,
) -> str:
    should_deploy_apps = os.environ.get("DEPLOY_APPS", "False") == "true"

    if not should_deploy_apps:
        pytest.skip("`DEPLOY_APPS` does not equal `true`")

    if not (run_on_ci and repo == "posit-dev/py-shiny"):
        pytest.skip("Not on CI and within posit-dev/py-shiny repo")

    app_dir = os.path.dirname(app_file_path)
    app_dir_name = os.path.basename(app_dir)

    # Use temporary directory to avoid modifying the original app directory
    # This allows us to run tests in parallel when deploying apps both modify the same rsconnect config file
    with tempfile.TemporaryDirectory("deploy_app") as tmpdir:

        # Creating a dir with same name instead of tmp to avoid issues
        # when deploying app to shinyapps.io using rsconnect package
        # since the rsconnect/*.json file needs the app_dir name to be same
        tmp_app_dir = os.path.join(tmpdir, app_dir_name)
        os.mkdir(tmp_app_dir)
        shutil.copytree(app_dir, tmp_app_dir, dirs_exist_ok=True)
        if should_use_github_requirements_txt:
            write_github_requirements_txt(tmp_app_dir)
        else:
            write_pypi_requirements_txt(tmp_app_dir)

        deployment_function = {
            "connect": deploy_to_connect,
            "shinyapps": deploy_to_shinyapps,
        }[location]

        pre_deployment_time = time.time()
        url = deployment_function(app_name, tmp_app_dir)
        tmp_rsconnect_config = os.path.join(
            tmp_app_dir, "rsconnect-python", f"{os.path.basename(tmp_app_dir)}.json"
        )
        assert_rsconnect_file_updated(tmp_rsconnect_config, pre_deployment_time)

        return url


def local_deploys_app_url_fixture(
    app_name: str,
    scope: ScopeName = "module",
):
    @pytest.fixture(scope=scope, params=[*deploy_locations, LOCAL_LOCATION])
    def fix_fn(request: pytest.FixtureRequest):

        app_file = os.path.join(os.path.dirname(request.path), "app.py")
        deploy_location = request.param

        if deploy_location == LOCAL_LOCATION:
            shinyapp_proc_gen = shiny_app_gen(app_file)
            # Return the `url`
            yield next(shinyapp_proc_gen).url
        elif deploy_location in deploy_locations:

            if deploy_location == "connect" and not (server_url and api_key):
                pytest.skip("Connect server url or api key not found. Cannot deploy.")
            if (
                deploy_location == "shinyapps"
                and shinyappsio_name
                and shinyappsio_token
                and shinyappsio_secret
            ):
                pytest.skip(
                    "Shinyapps.io name, token or secret not found. Cannot deploy."
                )

            app_url = deploy_app(
                app_file,
                deploy_location,
                app_name,
            )
            yield app_url

        else:
            raise ValueError(
                "Deploy location not a known location: '", deploy_location, "'"
            )

    return fix_fn
