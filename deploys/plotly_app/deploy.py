import os
import re
import subprocess

from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

server_url = os.environ.get("CONNECT_SERVER_URL")
api_key = os.environ.get("CONNECT_SERVER_API_KEY")
account_name = os.environ.get("SHINYAPPSIO_ACCOUNT_NAME")
name = os.environ.get("SHINYAPPSIO_NAME")
token = os.environ.get("SHINYAPPSIO_TOKEN")
secret = os.environ.get("SHINYAPPSIO_SECRET")


def deploy_to_connect(app_name: str, app_file_path: str) -> str:
    # Deploy to connect server
    connect_server_deploy = f"rsconnect deploy shiny {app_file_path} --server {server_url} --api-key {api_key} --title {app_name}"
    subprocess.run(connect_server_deploy, check=True, shell=True)
    # look up content url in connect server once app is deployed
    connect_server_lookup_command = f"rsconnect content search --server {server_url} --api-key {api_key} --title-contains {app_name}"
    url = subprocess.run(
        connect_server_lookup_command,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        shell=True,
    )
    # parse out the content url from the output of the lookup command
    for line in url.stdout.splitlines():
        if "content_url" in line:
            url_pattern = r'"content_url": "([^"]+)"'
            match = re.search(url_pattern, line)
            if match:
                url = match.group(1)
    return url


def deploy_to_shinyapps(app_name: str, app_file_path: str) -> str:
    # Deploy to shinyapps.io
    shinyapps_deploy = f"rsconnect deploy shiny {app_file_path} --account {name} --token {token} --secret {secret} --title {app_name}"
    subprocess.run(shinyapps_deploy, shell=True, check=True)
    return f"https://{account_name}.shinyapps.io/{app_name}/"


def deploy(location: str, app_name: str, app_file_path: str) -> str:
    deployment_functions = {
        "connect": deploy_to_connect,
        "shinyapps": deploy_to_shinyapps,
    }
    deployment_function = deployment_functions.get(location)
    if deployment_function:
        url = deployment_function(app_name, app_file_path)
    else:
        raise ValueError("Unknown deploy location. Cannot deploy.")
    return url
