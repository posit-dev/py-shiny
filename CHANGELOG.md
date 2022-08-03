# Change Log for Shiny (for Python)

All notable changes to Shiny for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

### Bug fixes

* Fixed #290: `@render.plot` now works as intended inside `@module.server`. (#292) 
* Fixed #289: `input_selectize()` now resolves the input id before using for other id-like attributes (#291)

## [0.2.4] - 2022-08-01

### Bug fixes

* Fixed #287: Running `shiny static` on Windows failed with `PermissionError`. (#288)

## [0.2.3] - 2022-07-28

### Bug fixes

* Fixed #281: Directory creation for Shinylive assets could fail if the parent directory did not exist. (#283)

## [0.2.2] - 2022-07-27

Initial release of Shiny for Python https://shiny.rstudio.com/py/
