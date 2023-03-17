import os
import typing
from pathlib import PurePath

import pytest
from conftest import run_shiny_app
from playwright.sync_api import ConsoleMessage, Page

here = PurePath(__file__).parent


def get_apps(path: PurePath) -> typing.List[str]:
    app_paths: typing.List[str] = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            app_path = os.path.join(item_path, "app.py")
            if os.path.isfile(app_path):
                app_paths.append(app_path)
    return app_paths


example_apps: typing.List[str] = [
    *get_apps(here / "../../examples"),
    *get_apps(here / "../../shiny/examples"),
]


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
@pytest.mark.parametrize("ex_app_path", example_apps)
def test_examples(page: Page, ex_app_path: str) -> None:
    app = run_shiny_app(ex_app_path, wait_for_start=True)

    console_errors: typing.List[str] = []

    def on_console_msg(msg: ConsoleMessage) -> None:
        if msg.type == "error":
            console_errors.append(msg.text)

    page.on("console", on_console_msg)

    # Makes sure the app is closed when exiting the code block
    with app:
        page.goto(app.url)

        if "brownian" in ex_app_path or "ui-func" in ex_app_path:
            # Apps are constantly invalidating and will not stabilize
            # Instead, wait for 500 milliseconds
            page.wait_for_timeout(500)
        else:
            # Wait for app to stop updating
            wait_for_idle_app(page, timeout=5 * 1000)

        assert len(console_errors) == 0, (
            "In app "
            + ex_app_path
            + " had JavaScript console errors!\n"
            + "* ".join(console_errors)
        )
