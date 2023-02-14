# Change Log for Shiny (for Python)

All notable changes to Shiny for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

### New features

* The `req()` function now returns its first argument (assuming none of its arguments are falsey). This lets you perform validation on expressions as you assign, return, or pass them, without needing to introduce a separate statement just to call `req()`.

### Bug fixes

* The `width` parameters for `input_select` and `input_slider` now work properly. (Thanks, @bartverweire!) (#386)

### Other changes


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

Initial release of Shiny for Python https://shiny.rstudio.com/py/
