import os
import sys
import typing
from pathlib import PurePath
from typing import Literal

import pytest
from conftest import run_shiny_app
from playwright.sync_api import ConsoleMessage, Page

here_tests_e2e_examples = PurePath(__file__).parent
here_root = here_tests_e2e_examples.parent.parent.parent

is_interactive = hasattr(sys, "ps1")
reruns = 1 if is_interactive else 3


def get_apps(path: str) -> typing.List[str]:
    full_path = here_root / path
    app_paths: typing.List[str] = []
    for folder in os.listdir(full_path):
        folder_path = os.path.join(full_path, folder)
        if os.path.isdir(folder_path):
            app_path = os.path.join(folder_path, "app.py")
            if os.path.isfile(app_path):
                # Return relative app path
                app_paths.append(os.path.join(path, folder, "app.py"))
    return app_paths


example_apps: typing.List[str] = [
    *get_apps("examples"),
    *get_apps("shiny/api-examples"),
]

app_idle_wait = {"duration": 300, "timeout": 5 * 1000}
app_hard_wait: typing.Dict[str, int] = {
    "brownian": 250,
    "ui-func": 250,
}
app_allow_shiny_errors: typing.Dict[
    str, typing.Union[Literal[True], typing.List[str]]
] = {
    "SafeException": True,
    "global_pyplot": True,
    "static_plots": [
        # acceptable warning
        "PlotnineWarning: Smoothing requires 2 or more points",
        "RuntimeWarning: divide by zero encountered",
        "UserWarning: This figure includes Axes that are not compatible with tight_layout",
    ],
}
app_allow_external_errors: typing.List[str] = [
    # plotnine: https://github.com/has2k1/plotnine/issues/713
    # mizani: https://github.com/has2k1/mizani/issues/34
    # seaborn: https://github.com/mwaskom/seaborn/issues/3457
    "FutureWarning: is_categorical_dtype is deprecated",
    "if pd.api.types.is_categorical_dtype(vector",  # continutation of line above
    # plotnine: https://github.com/has2k1/plotnine/issues/713#issuecomment-1701363058
    "FutureWarning: The default of observed=False is deprecated",
    # seaborn: https://github.com/mwaskom/seaborn/pull/3355
    "FutureWarning: use_inf_as_na option is deprecated",
    "pd.option_context('mode.use_inf_as_na",  # continutation of line above
]
app_allow_js_errors: typing.Dict[str, typing.List[str]] = {
    "brownian": ["Failed to acquire camera feed:"],
}


# Altered from `shinytest2:::app_wait_for_idle()`
# https://github.com/rstudio/shinytest2/blob/b8fdce681597e9610fc078aa6e376134c404f3bd/R/app-driver-wait.R
def wait_for_idle_js(duration: int = 500, timeout: int = 30 * 1000) -> str:
    return """
        let duration = %s; // time needed to be idle
        let timeout = %s; // max total time
        console.log("Making promise to run");
        new Promise((resolve, reject) => {
            console.log('Waiting for Shiny to be stable');
            const cleanup = () => {
                $(document).off('shiny:busy', busyFn);
                $(document).off('shiny:idle', idleFn);
                clearTimeout(timeoutId);
                clearTimeout(idleId);
            }
            let timeoutId = setTimeout(() => {
                cleanup();
                reject('Shiny did not become stable within ' + timeout + 'ms');
            }, +timeout); // make sure timeout is number
            let idleId = null;
            const busyFn = () => {
                // clear timeout. Calling with `null` is ok.
                clearTimeout(idleId);
            };
            const idleFn = () => {
                const fn = () => {
                    // Made it through the required duration
                    // Remove event listeners
                    cleanup();
                    console.log('Shiny has been idle for ' + duration + 'ms');
                    // Resolve the promise
                    resolve();
                };
                // delay the callback wrapper function
                idleId = setTimeout(fn, +duration);
            };
            // set up individual listeners for this function.
            $(document).on('shiny:busy', busyFn);
            $(document).on('shiny:idle', idleFn);
            // if already idle, call `idleFn` to kick things off.
            if (! $("html").hasClass("shiny-busy")) {
                idleFn();
            }
        })
    """ % (
        duration,
        timeout,
    )


def wait_for_idle_app(
    page: Page, duration: int = 500, timeout: int = 30 * 1000
) -> None:
    page.evaluate(
        wait_for_idle_js(duration, timeout),
    )


# Run this test for each example app
@pytest.mark.examples
@pytest.mark.parametrize("ex_app_path", example_apps)
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
def test_examples(page: Page, ex_app_path: str) -> None:
    app = run_shiny_app(here_root / ex_app_path, wait_for_start=True)

    console_errors: typing.List[str] = []

    def on_console_msg(msg: ConsoleMessage) -> None:
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", on_console_msg)

    # Makes sure the app is closed when exiting the code block
    with app:
        page.goto(app.url)

        app_name = os.path.basename(os.path.dirname(ex_app_path))

        if app_name in app_hard_wait.keys():
            # Apps are constantly invalidating and will not stabilize
            # Instead, wait for specific amount of time
            page.wait_for_timeout(app_hard_wait[app_name])
        else:
            # Wait for app to stop updating
            wait_for_idle_app(
                page,
                duration=app_idle_wait["duration"],
                timeout=app_idle_wait["timeout"],
            )

        # Check for py-shiny errors
        error_lines = str(app.stderr).splitlines()

        # Remove any errors that are allowed
        error_lines = [
            line
            for line in error_lines
            if not any([error_txt in line for error_txt in app_allow_external_errors])
        ]

        # Remove any app specific errors that are allowed
        if app_name in app_allow_shiny_errors:
            app_allowable_errors = app_allow_shiny_errors[app_name]
        else:
            app_allowable_errors = []

        # If all errors are not allowed, check for unexpected errors
        if isinstance(app_allowable_errors, list):
            app_allowable_errors = (
                # Remove ^INFO lines
                ["INFO:"]
                # Remove any known errors caused by external packages
                + app_allow_external_errors
                # Remove any known errors allowed by the app
                + app_allowable_errors
            )

            # If there is an array of allowable errors, remove them from errors. Ex: `PlotnineWarning`
            error_lines = [
                line
                for line in error_lines
                if not any([error_txt in line for error_txt in app_allowable_errors])
            ]
            if len(error_lines) > 0:
                print("\n".join(error_lines))
            assert len(error_lines) == 0

        # Check for JavaScript errors
        if app_name in app_allow_js_errors:
            # Remove any errors that are allowed
            console_errors = [
                line
                for line in console_errors
                if not any(
                    [error_txt in line for error_txt in app_allow_js_errors[app_name]]
                )
            ]
        assert len(console_errors) == 0, (
            "In app "
            + ex_app_path
            + " had JavaScript console errors!\n"
            + "* ".join(console_errors)
        )
