# Barret TODO's



* Barret
  * √ CardItem to have `render()` method instead of `get_item()`
  * √ delete fillabe check in `card_body()`
  * √ card_title() / card_header(); remove `_` from `container`
  * √ card_item() return value should be `image`
  * √ layout_sidebar() border should be a bool. currently trinary
  * √ htmltools fill dependency should use htmltools pkg version
  * √ look at diff of bslib from cran till now and walk through it
    * https://github.com/rstudio/bslib/compare/v0.4.2...main
    * At `card()`
    * Add method to join args and kwargs and sep
  * √ Remove `class_` from `bind_fill_role()` methods
  * √ page_sidebar fill / fillable
  * √ Update all examples to use new layout methods
    * Have deprecations for helper methods
      * `panel_sidebar()`
      * `panel_main()`
  * Document all experimental methods
    * Including nav_hidden https://github.com/rstudio/py-shiny/issues/498
  * Get out of `shiny.experiemental` and into `shiny`
  * Update (and/or coordinate) website docs
    * Users should know about new features
    * quartodocs configs


√ Automate dependencies from bslib into experimental

* TagifiedTag
  * https://github.com/rstudio/py-shiny/pull/338#issuecomment-1262964933

htmltools
* tagQuery find from root
  * finish / test all methods to handle `selected=NULL`
  * print method given `selected=NULL`
  * fix tests
  * get carson approval
  * document
    * vignette
    * tagquery docs
    * how to restore previous behavior
      * `.myclass` -> `* .myclass`
* √ `div()`


#################################

# Done

Port these methods from `{bslib}`

* √ Page
  * `page_navbar()`
    * https://github.com/rstudio/bslib/compare/v0.4.2...main#diff-579d0441768b84534d900cf5a52a63bccfdc5ecdb68430426d49e692ba47e794R87

* √ Navs
  * https://github.com/rstudio/bslib/compare/v0.4.2...main#diff-4443e29946f11f5721101ddf87ecac6130a08f10888d0b3907bfd13758ff4c04
  * √ page_navbar
  * √ navs_tab_card
  * √ navs_pill_card
  * √ navs_card_body

* √ Fill
  * https://github.com/rstudio/bslib/compare/v0.4.2...main#diff-dc4ed36da192ddeea9da8bfb6cf93de4ba4eede051a744e7a1091fb04389374b
  * √`is_fill()`
  * √`is_fillable()`
  * √`is_fill_carrier()`
  * √`as_fill()`
  * √`as_fillable()`
  * √`as_fill_carrier()`
  * √`undo_fill()`



# June 13, 2021 - Dcoumentation

* Finish docstrings (several parameters have TODOs on them)
* Update shiny.rstudio.com/py/docs/overview.html
* Update shiny.rstudio.com/py/docs/ui-page-layouts.html
* Update/fix example on the home page to use page_sidebar().
