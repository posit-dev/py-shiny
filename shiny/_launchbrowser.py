import webbrowser

from ._hostenv import get_proxy_url


def launch_browser(host: str, port: int) -> None:
    url = get_proxy_url(f"http://{host}:{port}/")
    webbrowser.open(url, 1)
