from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Callable, TypeVar

import pytest
import requests
from conftest import ScopeName, local_app_fixture_gen

LOCAL_LOCATION = "local"

__all__ = (
    "create_deploys_app_url_fixture",
    "skip_if_not_chrome",
)

# connect
server_url = os.environ.get("DEPLOY_CONNECT_SERVER_URL")
api_key = os.environ.get("DEPLOY_CONNECT_SERVER_API_KEY")
# shinyapps.io
name = os.environ.get("DEPLOY_SHINYAPPS_NAME")
token = os.environ.get("DEPLOY_SHINYAPPS_TOKEN")
secret = os.environ.get("DEPLOY_SHINYAPPS_SECRET")


deploy_locations = ["connect", "shinyapps"]

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


def exception_swallower(
    function: Callable[[str, str], str]
) -> Callable[[str, str], str]:
    def wrapper(app_name: str, app_dir: str) -> str:
        runtime_e: Exception | None = None
        try:
            return function(app_name, app_dir)
        except Exception as e:
            runtime_e = e
        if isinstance(runtime_e, Exception):
            raise RuntimeError("Failed to deploy to server.")

    return wrapper


def run_command(cmd: str) -> str:
    output = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        shell=True,
    )
    return output.stdout


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
        raise RuntimeError("Failed to change visibility of app.")
    return url


quiet_deploy_to_connect = exception_swallower(deploy_to_connect)


# TODO-future: Supress web browser from opening after deploying - https://github.com/rstudio/rsconnect-python/issues/462
def deploy_to_shinyapps(app_name: str, app_dir: str) -> str:
    # Deploy to shinyapps.io
    shinyapps_deploy = f"rsconnect deploy shiny {app_dir} --account {name} --token {token} --secret {secret} --title {app_name} --verbose"
    run_command(shinyapps_deploy)
    return f"https://{name}.shinyapps.io/{app_name}/"


quiet_deploy_to_shinyapps = exception_swallower(deploy_to_shinyapps)


# Since connect parses python packages, we need to get latest version of shiny on HEAD
def write_requirements_txt(app_dir: str) -> None:
    app_requirements_file_path = os.path.join(app_dir, "app_requirements.txt")
    requirements_file_path = os.path.join(app_dir, "requirements.txt")
    git_cmd = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    git_hash = git_cmd.stdout.decode("utf-8").strip()
    with open(app_requirements_file_path) as f:
        requirements = f.read()
    with open(requirements_file_path, "w") as f:
        f.write(f"{requirements}\n")
        f.write(f"git+https://github.com/posit-dev/py-shiny.git@{git_hash}\n")


def deploy_app(
    app_file_path: str,
    location: str,
    app_name: str,
) -> str:
    should_deploy_apps = os.environ.get("DEPLOY_APPS", "False") == "true"

    if not should_deploy_apps:
        pytest.skip("`DEPLOY_APPS` does not equal `true`")

    run_on_ci = os.environ.get("CI", "False") == "true"
    repo = os.environ.get("GITHUB_REPOSITORY", "unknown")
    branch_name = os.environ.get("GITHUB_HEAD_REF", "unknown")

    if (
        not run_on_ci
        or repo != "posit-dev/py-shiny"
        or not (branch_name.startswith("deploy") or branch_name == "main")
    ):
        pytest.skip("Not on CI or posit-dev/py-shiny repo or deploy* or main branch")
        raise RuntimeError()

    app_dir = os.path.dirname(app_file_path)
    write_requirements_txt(app_dir)

    deployment_function = {
        "connect": quiet_deploy_to_connect,
        "shinyapps": quiet_deploy_to_shinyapps,
    }[location]

    url = deployment_function(app_name, app_dir)
    return url


def create_deploys_app_url_fixture(
    app_name: str,
    scope: ScopeName = "module",
):
    @pytest.fixture(scope=scope, params=[*deploy_locations, LOCAL_LOCATION])
    def fix_fn(request: pytest.FixtureRequest):
        app_file = os.path.join(os.path.dirname(request.path), "app.py")
        deploy_location = request.param

        if deploy_location == LOCAL_LOCATION:
            shinyapp_proc_gen = local_app_fixture_gen(app_file)
            # Return the `url`
            yield next(shinyapp_proc_gen).url
        elif deploy_location in deploy_locations:
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
