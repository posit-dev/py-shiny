import json
import os
import shutil
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


@exception_swallower
def deploy_to_connect(app_name: str, app_file_path: str) -> str:
    if not api_key:
        raise RuntimeError("No api key found. Cannot deploy.")
    # Deploy to connect server
    connect_server_deploy = f"rsconnect deploy shiny {app_file_path} --server {server_url} --api-key {api_key} --title {app_name} --verbose"
    subprocess.run(
        connect_server_deploy,
        check=True,
        shell=True,
    )

    # look up content url in connect server once app is deployed
    connect_server_lookup_command = f"rsconnect content search --server {server_url} --api-key {api_key} --title-contains {app_name}"
    output = subprocess.run(
        connect_server_lookup_command,
        check=True,
        capture_output=True,
        text=True,
        shell=True,
    )

    url = json.loads(output.stdout)[0]["content_url"]
    app_id = json.loads(output.stdout)[0]["guid"]
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


quiet_deploy_to_connect = deploy_to_connect


# TODO-future: Supress web browser from opening after deploying - https://github.com/rstudio/rsconnect-python/issues/462
@exception_swallower
def deploy_to_shinyapps(app_name: str, app_file_path: str) -> str:
    # Deploy to shinyapps.io
    shinyapps_deploy = f"rsconnect deploy shiny {app_file_path} --account {name} --token {token} --secret {secret} --title {app_name} --verbose"
    subprocess.run(
        shinyapps_deploy,
        shell=True,
        check=True,
    )
    return f"https://{name}.shinyapps.io/{app_name}/"


quiet_deploy_to_shinyapps = deploy_to_shinyapps


def deploy(location: str, app_name: str, app_file_path: str) -> str:
    deployment_functions = {
        "connect": quiet_deploy_to_connect,
        "shinyapps": quiet_deploy_to_shinyapps,
    }
    deployment_function = deployment_functions.get(location)
    if deployment_function:
        url = deployment_function(app_name, app_file_path)
        try:
            shutil.rmtree(f"{app_file_path}/rsconnect-python")
        except OSError as e:
            print(f"Error: {e}")
    else:
        raise ValueError("Unknown deploy location. Cannot deploy.")
    return url
