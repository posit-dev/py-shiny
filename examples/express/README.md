## `shiny.express` examples

This folder contains a collection of examples illustrating `shiny.express` usage.

### Apps

* [`accordion_app.py`](accordion_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Faccordion_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Integrates `ui.accordion()` and `ui.accordion_panel()`.

* [`basic_app.py`](basic_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fbasic_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Basic app containing a `ui.input_slider()` and `ui.output_code()`.

* [`column_wrap_app.py`](basic_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fbasic_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Basic app containing a `ui.input_slider()` and `ui.output_code()`.

* [`expressify_app.py`](expressify_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fexpressify_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Demonstrates how to use `@expressify` to convert regular functions into _express_ compatible functions.

* [`hold_app.py`](hold_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fhold_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Demonstrates how to use `@hold` to prevent the app from updating.

* [`nav_app.py`](nav_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fnav_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Demonstrates how to use different navsets along with `ui.nav_panel()`.

* [`plot_app.py`](plot_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fplot_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Demonstrates how plot render methods are rendered in place.

* [`render_express_app.py`](render_express_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Frender_express_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * Demonstrates how to use `@render.express()` (similar to `@render.ui()`), but for _express_ functions.

* [`shared_app.py`](shared_app.py): <a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny&sourceRef=main&sourceRefType=branch&primaryFile=examples%2Fexpress%2Fshared_app.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' height="15px" /></a>
  * This app demonstrates how to use "global" variables that are shared across sessions.
  * This is useful if you want to load data just once and use it in multiple apps, or if you want to share data or reactives among apps.
