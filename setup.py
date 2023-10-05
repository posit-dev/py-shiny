from setuptools import setup

setup(
    data_files=[
        (
            "etc/jupyter/jupyter_server_config.d",
            ["jupyter-config/jupyter_server_config.d/shiny.notebook.json"],
        ),
    ],
)
