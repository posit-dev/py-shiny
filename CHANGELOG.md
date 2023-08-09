# Change Log for Shiny (for Python)

All notable changes to Shiny for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.5.1] - 2023-08-08

### Bug fixes

* Fixed #666: Added missing sidebar stylesheet dependency. (#667)


## [0.5.0] - 2023-08-01

### New features

* The new fast-scrolling data table/grid feature (`ui.output_data_frame`/`render.data_frame`) now has a filtering feature. To enable, pass the argument `filters=True` to the `render.DataTable` or `render.DataGrid` constructors. (#592)
* `shiny run` now takes a `--reload-dir <DIR>` argument that indicates a directory `--reload` should (recursively) monitor for changes, in addition to the app's parent directory. Can be used more than once. (#353)
* The default theme has been updated to use Bootstrap 5 with custom Shiny style enhancements. (#624)
* Added experimental UI `tooltip()`, `update_tooltip()`, and `toggle_tooltip()` for easy creation (and server-side updating) of [Bootstrap tooltips](https://getbootstrap.com/docs/5.2/components/tooltips/) (a way to display additional information when focusing (or hovering over) a UI element). (#629)


### Bug fixes

* Using `update_slider` to update a slider's value to a `datetime` object or other non-numeric value would result in an error. (#649)

### Other changes

* Documentation updates. (#591)
* Removed Python 3.7 support. (#590)


## [0.4.0] - 2023-06-26

### New features

* Added new fast-scrolling data table and data grid outputs. (#538)

* Added `include_js()` and `include_css()`, for easily including JS and CSS files in an application. (#127)

* Added sidebar, card, value box, and accordion methods into `shiny.experimental.ui`. (#481)

* Added `fill` and `fillable` methods into `shiny.experimental.ui`. If `fill` is `True`, then the UI component is allowed to expand into the parent container. If `fillable` is `True`, then the UI component will allow its content to expand. Both `fill` on the child component and `fillable` on the parent component must be `True` for the child component to expand. (#481)

* Added sidebar methods into `shiny.experimental.ui`. `shiny.experimental.ui.layout_sidebar()` does not require `ui.panel_main()` and `ui.panel_sidebar()`. These two methods have been deprecated. `x.ui.page_navbar()`, `x.ui.navset_bar()`, `x.navset_tab_card()`, and `x.navset.pill_card()` added `sidebar=` support. (#481)

* feat(sidebar): `ui.layout_sidebar()` internally uses `x.ui.layout_sidebar()`, enabling filling layout features. (#568)


### Bug fixes

* Fixed #496: Previously, when `shiny run --reload` was used, the app would only reload when a .py file changed. Now it will reload when .py, .css, .js, and .html files change. (#505)

* Closed #535: Added a meta viewport tag, so that page layout will adapt to mobile device screens. (#540)

## [0.3.3] - 2023-04-26

### New features

* Added `shiny.experimental` as a place to put experimental features. When using Shiny's experimental features, we recommend importing them by calling `import shiny.experimental as x`, so that all local function calls must start with `x` (e.g. `x.ui.card()`) to signify the method may be changed/removed without warning or future support. (#462)

* Added `penguins` example. (#462)

* The bootstrap HTMLDependency is now created using the dev version of `{bslib}` to get the latest features. (#462)

* Added `shiny.experimental.ui.input_text_area()`, which supports auto-resizing height to fit the content when `autoresize=True`. (#463)

### Other changes

* `shiny.reactive.lock` is now exported. (#458)

## [0.3.2] - 2023-04-19

### Bug fixes

* Fixed #456: plot interaction with datetimes raised errors on 32-bit platforms. (#457)

### Other changes

* When pyright creates type stubs for shiny, it now will include types imported in `_typing_extensions.py`.


## [0.3.1] - 2023-04-18

### Bug fixes

* Fixed #443: Errors in streaming downloads previously resulted in a partially downloaded file; now Shiny responds with a `Transfer-Encoding: chunked` header, which allows the browser to detect the error and abort the download. (#447)

### Other changes

* `page_navbar` now accepts shinyswatch themes. (#455)


## [0.3.0] - 2023-04-03

### New features

* Added support for URL based HTMLDependencies. `{htmltools}` (v0.1.5.9001) added support for URL based HTMLDependencies in rstudio/py-htmltools#53.  (#437)


## [0.2.10] - 2023-03-11

### New features

* Added support for interacting with plots made with matplotlib, seaborn, and plotnine. (#392)

* The `req()` function now returns its first argument (assuming none of its arguments are falsey). This lets you perform validation on expressions as you assign, return, or pass them, without needing to introduce a separate statement just to call `req()`.

* Added `Input.__contains__` method, so that (for example) one could write an expression like `if "x" in inputs`. (#402)

### Bug fixes

* The `width` parameters for `input_select` and `input_slider` now work properly. (Thanks, @bartverweire!) (#386)

* When `input_select` or `input_selectize` were not given an explicit `select` argument, they always chose the first item, which is correct when `multiple=False`, but not when `multiple=True`. Now when `multiple=True`, the first item is no longer automatically selected. (#396)

### Other changes

* Switched to new types from htmltools 0.1.5. (#416)


## [0.2.9] - 2022-11-03

### Bug fixes

* Closed #240, #330: Fixed live examples with additional files. (#340)

* Fixed `shiny run` handling on Windows of absolute paths with drive letter, as in `shiny run c:/myapp/app.py`. (#370)


## [0.2.8] - 2022-10-20

### Bug fixes

* `panel_conditional` now works correctly inside of Shiny modules. (Thanks, @gcaligari!) (#336)

* Fix compatibility with Uvicorn 0.19.0 (#357)


## [0.2.7] - 2022-09-27

### New features

* `shiny run` now takes a `--launch-browser` argument that causes the default web browser to be launched after the app is successfully loaded. Also, the `--port` argument now interprets a value of `0` as "listen on a random port". (#329)

### Other changes

* Updated API document generation with updated paths to work with new version of Shinylive. (#331)


## [0.2.6] - 2022-09-02

### New features

* Closed [#312](https://github.com/rstudio/py-shiny/issues/312): Matplotlib plots in a `@render.plot` can now use the global figure, instead of returning a `figure` object. ([#314](https://github.com/rstudio/py-shiny/pull/314))

* Disabled `shiny static` command, in favor of `shinylive export` from the shinylive package. ([#326](https://github.com/rstudio/py-shiny/pull/326))


## [0.2.5] - 2022-08-12

### New features

* Closed [#269](https://github.com/rstudio/py-shiny/issues/269): The UI for a `shiny.App` object can now be provided as a function. ([#299](https://github.com/rstudio/py-shiny/pull/299))
* When a Shinylive deployment is made with `shiny static`, it the deployment code is now delegated to Shinylive. ([#310](https://github.com/rstudio/py-shiny/pull/310))

### Bug fixes

* Fixed [#279](https://github.com/rstudio/py-shiny/issues/279): When a Shiny application is mounted to a Starlette route, reactivity did not work. ([#294](https://github.com/rstudio/py-shiny/pull/294))
* Fixed [#290](https://github.com/rstudio/py-shiny/issues/290): `@render.plot` now works as intended inside `@module.server`. ([#292](https://github.com/rstudio/py-shiny/pull/292))
* Fixed [#289](https://github.com/rstudio/py-shiny/issues/289): `input_selectize()` now resolves the input id before using for other id-like attributes ([#291](https://github.com/rstudio/py-shiny/pull/291))

## [0.2.4] - 2022-08-01

### Bug fixes

* Fixed [#287](https://github.com/rstudio/py-shiny/issues/287): Running `shiny static` on Windows failed with `PermissionError`. ([#288](https://github.com/rstudio/py-shiny/pull/288))

## [0.2.3] - 2022-07-28

### Bug fixes

* Fixed [#281](https://github.com/rstudio/py-shiny/issues/281): Directory creation for Shinylive assets could fail if the parent directory did not exist. ([#283](https://github.com/rstudio/py-shiny/pull/283))

## [0.2.2] - 2022-07-27

Initial release of Shiny for Python https://shiny.posit.co/py/
