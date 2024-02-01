import os
import sys
import typing
from pathlib import PurePath
from typing import Literal

from conftest import run_shiny_app
from playwright.sync_api import ConsoleMessage, Page

here_tests_e2e_examples = PurePath(__file__).parent
pyshiny_root = here_tests_e2e_examples.parent.parent.parent

is_interactive = hasattr(sys, "ps1")
reruns = 1 if is_interactive else 3
reruns_delay = 0


def get_apps(path: str) -> typing.List[str]:
    full_path = pyshiny_root / path
    app_paths: typing.List[str] = []
    for folder in os.listdir(full_path):
        folder_path = os.path.join(full_path, folder)
        if os.path.isdir(folder_path):
            folder_files = os.listdir(folder_path)
            for file in folder_files:
                if os.path.isdir(os.path.join(folder_path, file)):
                    continue
                if not file.endswith(".py"):
                    continue
                if file == "app.py" or file.startswith("app-"):
                    # Return relative app path
                    app_paths.append(os.path.join(path, folder, file))
    return app_paths


app_idle_wait = {"duration": 300, "timeout": 5 * 1000}
app_hard_wait: typing.Dict[str, int] = {
    "examples/brownian": 250,
    "examples/ui-func": 250,
}
output_transformer_errors = [
    "ShinyDeprecationWarning: `shiny.render.transformer.output_transformer()`",
    "  super().__init__(",
    "  return OutputRenderer",
    # brownian example app
    "ShinyDeprecationWarning:",
    "shiny.render.transformer.output_transformer()",
]
express_warnings = ["Detected Shiny Express app. "]
app_allow_shiny_errors: typing.Dict[
    str, typing.Union[Literal[True], typing.List[str]]
] = {
    "api-examples/SafeException": True,
    "examples/global_pyplot": True,
    "examples/static_plots": [
        # acceptable warning
        "PlotnineWarning: Smoothing requires 2 or more points",
        "RuntimeWarning: divide by zero encountered",
        "UserWarning: This figure includes Axes that are not compatible with tight_layout",
    ],
    # Remove after shinywidgets accepts `Renderer` PR
    "api-examples/data_frame": [*output_transformer_errors],
    "api-examples/output_transformer": [*output_transformer_errors],
    "api-examples/render_express": [*express_warnings],
    "app-templates/multi-page": [*output_transformer_errors],
    "examples/airmass": [*output_transformer_errors],
    "examples/brownian": [*output_transformer_errors],
    "examples/model-score": [*output_transformer_errors],
    "deploys/plotly": [*output_transformer_errors],
}
app_allow_external_errors: typing.List[str] = [
    # TODO-garrick-future: Remove after fixing sidebar max_height_mobile warning
    "UserWarning: The `shiny.ui.sidebar(max_height_mobile=)`",
    "res = self.fn(*self.args, **self.kwargs)",
    # pandas >= 2.2.0
    # https://github.com/pandas-dev/pandas/blame/5740667a55aabffc660936079268cee2f2800225/pandas/core/groupby/groupby.py#L1129
    "FutureWarning: When grouping with a length-1 list-like",
    "sf: grouped.get_group",  # continutation of line above
    "FutureWarning:",
    "When grouping with a length-1 list-like",  # continutation of line above
    "data_subset = grouped_data.get_group(pd_key)",  # continutation of line above
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
    "examples/brownian": ["Failed to acquire camera feed:"],
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


def validate_example(page: Page, ex_app_path: str) -> None:
    app = run_shiny_app(pyshiny_root / ex_app_path, wait_for_start=True)

    console_errors: typing.List[str] = []

    def on_console_msg(msg: ConsoleMessage) -> None:
        if msg.type == "error":
            # Do not report missing favicon errors
            if msg.location["url"].endswith("favicon.ico"):
                return
            console_errors.append(msg.text)

    page.on("console", on_console_msg)

    # Makes sure the app is closed when exiting the code block
    with app:
        page.goto(app.url)

        app_name = os.path.basename(os.path.dirname(ex_app_path))
        short_app_path = f"{os.path.basename(os.path.dirname(os.path.dirname(ex_app_path)))}/{app_name}"

        if short_app_path in app_hard_wait.keys():
            # Apps are constantly invalidating and will not stabilize
            # Instead, wait for specific amount of time
            page.wait_for_timeout(app_hard_wait[short_app_path])
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
        if short_app_path in app_allow_shiny_errors:
            app_allowable_errors = app_allow_shiny_errors[short_app_path]
        else:
            app_allowable_errors = []

        # If all errors are not allowed, check for unexpected errors
        if app_allowable_errors is not True:
            if isinstance(app_allowable_errors, str):
                app_allowable_errors = [app_allowable_errors]
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
                if len(line.strip()) > 0
                and not any([error_txt in line for error_txt in app_allowable_errors])
            ]
            if len(error_lines) > 0:
                print("\nshort_app_path: " + short_app_path)
                print("\napp_allowable_errors :")
                print("\n".join(app_allowable_errors))
                print("\nError lines remaining:")
                print("\n".join(error_lines))
            assert len(error_lines) == 0

        # Check for JavaScript errors
        if short_app_path in app_allow_js_errors:
            # Remove any errors that are allowed
            console_errors = [
                line
                for line in console_errors
                if not any(
                    [
                        error_txt in line
                        for error_txt in app_allow_js_errors[short_app_path]
                    ]
                )
            ]
        assert len(console_errors) == 0, (
            "In app "
            + ex_app_path
            + " had JavaScript console errors!\n"
            + "* ".join(console_errors)
        )
