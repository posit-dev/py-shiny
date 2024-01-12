import json
import os
import subprocess
import typing

import requests

__all__ = ("deploy",)

# connect
server_url = os.environ.get("DEPLOY_CONNECT_SERVER_URL")
api_key = os.environ.get("DEPLOY_CONNECT_SERVER_API_KEY")
# shinyapps.io
name = os.environ.get("DEPLOY_SHINYAPPS_NAME")
token = os.environ.get("DEPLOY_SHINYAPPS_TOKEN")
secret = os.environ.get("DEPLOY_SHINYAPPS_SECRET")


def exception_swallower(
    function: typing.Callable[[str, str], str]
) -> typing.Callable[[str, str], str]:
    def wrapper(app_name: str, app_file_path: str) -> str:
        runtime_e: typing.Union[Exception, None] = None
        try:
            return function(app_name, app_file_path)
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


def deploy_to_connect(app_name: str, app_file_path: str) -> str:
    if not api_key:
        raise RuntimeError("No api key found. Cannot deploy.")

    # check if connect app is already deployed to avoid duplicates
    connect_server_lookup_command = f"rsconnect content search --server {server_url} --api-key {api_key} --title-contains {app_name}"
    app_details = run_command(connect_server_lookup_command)
    connect_server_deploy = f"rsconnect deploy shiny {app_file_path} --server {server_url} --api-key {api_key} --title {app_name} --verbose"
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
def deploy_to_shinyapps(app_name: str, app_file_path: str) -> str:
    # Deploy to shinyapps.io
    shinyapps_deploy = f"rsconnect deploy shiny {app_file_path} --account {name} --token {token} --secret {secret} --title {app_name} --verbose"
    run_command(shinyapps_deploy)
    return f"https://{name}.shinyapps.io/{app_name}/"


quiet_deploy_to_shinyapps = exception_swallower(deploy_to_shinyapps)


def deploy(location: str, app_name: str, app_file_path: str) -> str:
    deployment_functions = {
        "connect": quiet_deploy_to_connect,
        "shinyapps": quiet_deploy_to_shinyapps,
    }
    deployment_function = deployment_functions.get(location)
    if deployment_function:
        url = deployment_function(app_name, app_file_path)
    else:
        raise ValueError("Unknown deploy location. Cannot deploy.")
    return url


# Since connect parses python packages, we need to get latest version of shiny on HEAD
def write_requirements_txt(app_file_path: str) -> None:
    app_requirements_file_path = os.path.join(app_file_path, "app_requirements.txt")
    requirements_file_path = os.path.join(app_file_path, "requirements.txt")
    git_cmd = subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    git_hash = git_cmd.stdout.decode("utf-8").strip()
    with open(app_requirements_file_path) as f:
        requirements = f.read()
    with open(requirements_file_path, "w") as f:
        f.write(f"{requirements}\n")
        f.write(f"git+https://github.com/posit-dev/py-shiny.git@{git_hash}\n")
