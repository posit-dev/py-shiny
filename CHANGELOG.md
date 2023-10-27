# Change Log for Shiny (for Python)

All notable changes to Shiny for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [UNRELEASED]

### New features

* The `@output` decorator is no longer required for rendering functions; `@render.xxx` decorators now register themselves automatically. You can still use `@output` explicitly if you need to set specific output options (#747).
* Added support for integration with Quarto (#746).
* Added `shiny.render.renderer_components` decorator to help create new output renderers (#621).
* Added `shiny.experimental.ui.popover()`, `update_popover()`, and `toggle_popover()` for easy creation (and server-side updating) of [Bootstrap popovers](https://getbootstrap.com/docs/5.2/components/popovers/). Popovers are similar to tooltips, but are more persistent, and should primarily be used with button-like UI elements (e.g. `input_action_button()` or icons) (#680).
* Added CSS classes to UI input methods (#680) .
* `Session` objects can now accept an asynchronous (or synchronous) function for `.on_flush(fn=)`, `.on_flushed(fn=)`, and `.on_ended(fn=)` (#686).
* `App()` now allows `static_assets` to represent multiple paths. To do this, pass in a dictionary instead of a string (#763).
* The `showcase_layout` argument of `value_box()` now accepts one of three character values: `"left center"`, `"top right"`, `"bottom"`. (#772)
* `value_box()` now supports many new themes and styles, or fully customizable themes using the new `value_box_theme()` function. To reflect the new capabilities, we've replaced `theme_color` with a new `theme` argument. The previous argument will continue work as expected, but with a deprecation warning. (#772)

  In addition to the Bootstrap theme names (`primary` ,`secondary`, etc.), you can now use the main Boostrap colors (`purple`, `blue`, `red`, etc.). You can also choose to apply the color to the background or foreground by prepending a `bg-` or `text-` prefix to the theme or color name. Finally, we've also added new gradient themes allowing you to pair any two color names as `bg-gradient-{from}-{to}` (e.g., `bg-gradient-purple-blue`).

  These named color themes aren't limited to value boxes: because they're powered by small utility classes, you can use them anywhere within your bslib-powered UI.

* Added `shiny.ui.showcase_bottom()`, a new `shiny.ui.value_box()` layout that places the showcase below the value box `title` and `value`, perfect for a full-bleed plot. (#772)
### API changes

* Added `shiny.ui.navset_underline()` and `shiny.ui.navset_card_underline()` whose navigation container is similar to `shiny.ui.navset_tab()` and `shiny.ui.navset_card_tab()` respectively, but its active/focused navigation links are styled with an underline. (#772)
* `shiny.ui.layout_column_wrap(width, *args)` was rearranged to `shiny.ui.layout_column_wrap(*args, width)`. Now, `width` will default to `200px` is no value is provided. (#772)
* `shiny.ui.showcase_left_center()` and `shiny.ui.showcase_top_right()` no longer take two values for the `width` argument. Instead, they now take a single value (e.g., `width = "30%"`) representing the width of the showcase are in the value box. Furthermore, they've both gained `width_full_screen` arguments that determine the width of the showcase area when the value box is expanded to fill the screen. (#772)


* TODO-barret-API; `shiny.ui.panel_main()` and `shiny.ui.panel_sidebar()` are deprecated in favor of new API for `shiny.ui.layout_sidebar()`. Please use `shiny.ui.sidebar()` to construct a sidebar and supply it (along with the main content) to `shiny.ui.layout_sidebar(*args, **kwargs)`. (#680)

#### API relocations

* `shiny.ui`'s `navset_pill_card()` and `navset_tab_card()` have been renamed to `navset_card_pill()` and `navset_card_tab()` respectively (#492).

The following methods have been moved from `shiny.experimental.ui` and integrated into `shiny.ui` (final locations under `shiny.ui` are displayed) (#680):

* Sidebar - Sidebar layout or manipulation
  * `sidebar()`, `page_sidebar()`, `toggle_sidebar()`, `layout_sidebar()`, `Sidebar`
* Filling layout - Allow UI components to expand into the parent container and/or allow its content to expand
  * `page_fillable()`, `fill.as_fillable_container()`, `fill.as_fill_item()`, `fill.is_fillable_container()`, `fill.is_fill_item()`, `fill.remove_all_fill()`
  * `output_plot(fill=)`, `output_image(fill=)`, `output_ui(fill=, fillable=)`
* CSS units - CSS units and padding
  * `css.as_css_unit()`, `css.as_css_padding()`, `css.CssUnit`
* Tooltip - Hover-based context UI element
  * `tooltip()`, `toggle_tooltip()`, `update_tooltip()`
* Popover - Click-based context UI element
  * `popover()`, `toggle_popover()`, `update_popover()`
* Accordion - Vertically collapsible UI element
  * `accordion()`, `accordion_panel()`, `accordion_panel_close()`, `accordion_panel_insert()`, `accordion_panel_open()`, `accordion_panel_remove()`, `accordion_panel_set()`, `update_accordion_panel()`, `Accordion`, `AccordionPanel`
* Card - A general purpose container for grouping related UI elements together
  * `card()`, `card_header()`, `card_footer()`, `CardItem`
* Valuebox - Opinionated container for displaying a value and title
  * `valuebox()`
  * `showcase_left_center()`
  * `showcase_top_right()`
* Navs - Navigation within a page
  * `navset_bar()`, `navset_tab_card()`, `navset_pill_card()`
  * `page_navbar(sidebar=, fillable=, fillable_mobile=, gap=, padding=)`, `navset_card_tab(sidebar=)`, `navset_card_pill(sidebar=)`, `navset_bar(sidebar=, fillable=, gap=, padding=)`
* Layout - Layout of UI elements
  * `layout_column_wrap()`
* Inputs - UI elements for user input
  * `toggle_switch()`
  * `input_text_area(autoresize=)`

If a ported method is called from `shiny.experimental.ui`, a deprecation warning will be displayed.

Methods still under consideration in `shiny.experimental.ui`:
* `card(wrapper=)`: A function (which returns a UI element) to call on unnamed arguments in `card(*args)` which are not already `shiny.ui.CardItem` objects.
* `card_body()`: A container for grouping related UI elements together
* `card_image()`: A general container for an image within a `shiny.ui.card`.
* `card_title()`: A general container for the "title" of a `shiny.ui.card`.


#### API removals

* `shiny.experimental.ui.FillingLayout` has been removed. (#481)
* `shiny.experimental.ui.as_width_unit()` has been made defunkt. Please remove it from your code. (#772)
* Support for `min_height=`, `max_height=`, and `gap=` in `shiny.experimental.ui.as_fillable_container()` and `as_fill_item()` has been removed. (#481)
* `shiny.experimental.ui.TagCallable` has been deprecated. Its type is equivalent to `htmltools.TagFunction`. (#680)
* `shiny.eperimental.ui.as_fill_carrier()` and `shiny.eperimental.ui.is_fill_carrier()` have been deprecated. Please use `shiny.ui.fill.as_fill_item()` and `shiny.ui.fill.as_fillable_container()` or `shiny.ui.fill.is_fill_item()` and `shiny.ui.fill.is_fillable_container()` respectively in combination to achieve similar behavior. (#680)

### Bug fixes

* Fixed #646: Wrap bare value box value in `<p />` tags. (#668)
* Fixed #676: The `render.data_frame` selection feature was underdocumented and buggy (sometimes returning `None` as a row identifier if the pandas data frame's index had gaps in it). With this release, the selection is consistently a tuple of the 0-based row numbers of the selected rows--or `None` if no rows are selected. (#677)
* Added tests to verify that ui input methods, ui labels, ui update (value) methods, and ui output methods work within modules (#696).
* Adjusted the `@render.plot` input type to be `object` to allow for any object (if any) to be returned (#712).
* In `layout_column_wrap()`, when `width` is a CSS unit -- e.g. `width = "400px"` or `width = "25%"` -- and `fixed_width = FALSE`, `layout_column_wrap()` will ensure that the columns are at least `width` wide, unless the parent container is narrower than `width`. (#772)

### Other changes

* `layout_sidebar()` now uses an `<aside>` element for the sidebar's container and a `<header>` element for the sidebar title. The classes of each element remain the same, but the semantic meaning of the elements is now better reflected in the HTML markup.
* `layout_sidebar()` no longer gives the sidebar main content area the `role="main"` attribute.


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

* Closed [#312](https://github.com/posit-dev/py-shiny/issues/312): Matplotlib plots in a `@render.plot` can now use the global figure, instead of returning a `figure` object. ([#314](https://github.com/posit-dev/py-shiny/pull/314))

* Disabled `shiny static` command, in favor of `shinylive export` from the shinylive package. ([#326](https://github.com/posit-dev/py-shiny/pull/326))


## [0.2.5] - 2022-08-12

### New features

* Closed [#269](https://github.com/posit-dev/py-shiny/issues/269): The UI for a `shiny.App` object can now be provided as a function. ([#299](https://github.com/posit-dev/py-shiny/pull/299))
* When a Shinylive deployment is made with `shiny static`, it the deployment code is now delegated to Shinylive. ([#310](https://github.com/posit-dev/py-shiny/pull/310))

### Bug fixes

* Fixed [#279](https://github.com/posit-dev/py-shiny/issues/279): When a Shiny application is mounted to a Starlette route, reactivity did not work. ([#294](https://github.com/posit-dev/py-shiny/pull/294))
* Fixed [#290](https://github.com/posit-dev/py-shiny/issues/290): `@render.plot` now works as intended inside `@module.server`. ([#292](https://github.com/posit-dev/py-shiny/pull/292))
* Fixed [#289](https://github.com/posit-dev/py-shiny/issues/289): `input_selectize()` now resolves the input id before using for other id-like attributes ([#291](https://github.com/posit-dev/py-shiny/pull/291))

## [0.2.4] - 2022-08-01

### Bug fixes

* Fixed [#287](https://github.com/posit-dev/py-shiny/issues/287): Running `shiny static` on Windows failed with `PermissionError`. ([#288](https://github.com/posit-dev/py-shiny/pull/288))

## [0.2.3] - 2022-07-28

### Bug fixes

* Fixed [#281](https://github.com/posit-dev/py-shiny/issues/281): Directory creation for Shinylive assets could fail if the parent directory did not exist. ([#283](https://github.com/posit-dev/py-shiny/pull/283))

## [0.2.2] - 2022-07-27

Initial release of Shiny for Python https://shiny.posit.co/py/
