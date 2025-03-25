"""Tests for"""

import contextlib
import random
import textwrap
from typing import Generator

import pytest
from htmltools import TagList

from shiny import ui
from shiny._deprecated import ShinyDeprecationWarning
from shiny._utils import private_seed
from shiny.ui._navs import (
    NavbarOptions,
    navbar_options,
    navbar_options_resolve_deprecated,
)


# Fix the randomness of these functions to make the tests deterministic
@contextlib.contextmanager
def private_seed_n(n: int = 0) -> Generator[None, None, None]:
    with private_seed():
        random.seed(n)
        yield


a = ui.nav_panel("a", "a")
b = ui.nav_panel("b", "b")
c = ui.nav_panel("c", "c")
menu = ui.nav_menu(
    "Menu",
    c,
    "----",
    "Plain text",
    "----",
    ui.nav_control("Other item"),
)


def test_navset_tab_markup():
    with private_seed_n():
        x = ui.navset_tab(a, b, ui.nav_control("Some item"), menu)

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <ul class="nav nav-tabs" data-tabsetid="886440">
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link active" href="#tab-886440-0">a</a>
          </li>
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="b" role="tab" class="nav-link" href="#tab-886440-1">b</a>
          </li>
          <li>Some item</li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle " data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
            <ul class="dropdown-menu" data-tabsetid="404958">
              <li>
                <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item" href="#tab-404958-0">c</a>
              </li>
              <li class="dropdown-divider"></li>
              <li class="dropdown-header">Plain text</li>
              <li class="dropdown-divider"></li>
              <li>Other item</li>
            </ul>
          </li>
        </ul>
        <div class="tab-content" data-tabsetid="886440">
          <div class="tab-pane active" role="tabpanel" data-value="a" id="tab-886440-0">a</div>
          <div class="tab-pane" role="tabpanel" data-value="b" id="tab-886440-1">b</div>
          <div class="tab-pane" role="tabpanel" data-value="c" id="tab-404958-0">c</div>
        </div>"""
    )


def test_navset_pill_markup():
    with private_seed_n():
        x = ui.navset_pill(menu, a, id="navset_pill_id")

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <ul class="nav nav-pills shiny-tab-input" id="navset_pill_id" data-tabsetid="886440">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
            <ul class="dropdown-menu" data-tabsetid="404958">
              <li>
                <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-404958-0">c</a>
              </li>
              <li class="dropdown-divider"></li>
              <li class="dropdown-header">Plain text</li>
              <li class="dropdown-divider"></li>
              <li>Other item</li>
            </ul>
          </li>
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link" href="#tab-886440-1">a</a>
          </li>
        </ul>
        <div class="tab-content" data-tabsetid="886440">
          <div class="tab-pane active" role="tabpanel" data-value="c" id="tab-404958-0">c</div>
          <div class="tab-pane" role="tabpanel" data-value="a" id="tab-886440-1">a</div>
        </div>"""
    )


def test_navset_card_pill_markup():
    with private_seed_n():
        x = ui.navset_card_pill(
            a,
            ui.nav_menu("Menu", c),
            b,
            selected="c",
        )

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <div class="card bslib-card bslib-mb-spacing html-fill-item html-fill-container" data-bslib-card-init="">
          <div class="card-header">
            <ul class="nav nav-pills card-header-pills" data-tabsetid="886440">
              <li class="nav-item">
                <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link" href="#tab-886440-0">a</a>
              </li>
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
                <ul class="dropdown-menu" data-tabsetid="404958">
                  <li>
                    <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-404958-0">c</a>
                  </li>
                </ul>
              </li>
              <li class="nav-item">
                <a data-bs-toggle="tab" data-toggle="tab" data-value="b" role="tab" class="nav-link" href="#tab-886440-2">b</a>
              </li>
            </ul>
          </div>
          <div class="card-body bslib-gap-spacing html-fill-item html-fill-container" style="margin-top:auto;margin-bottom:auto;flex:1 1 auto;">
            <div class="tab-content html-fill-item html-fill-container" data-tabsetid="886440">
              <div class="tab-pane html-fill-item html-fill-container bslib-gap-spacing" role="tabpanel" data-value="a" id="tab-886440-0" style="gap:0;padding:0;">a</div>
              <div class="tab-pane active html-fill-item html-fill-container bslib-gap-spacing" role="tabpanel" data-value="c" id="tab-404958-0" style="gap:0;padding:0;">c</div>
              <div class="tab-pane html-fill-item html-fill-container bslib-gap-spacing" role="tabpanel" data-value="b" id="tab-886440-2" style="gap:0;padding:0;">b</div>
            </div>
          </div>
          <script data-bslib-card-init="">window.bslib.Card.initializeAllCards();</script>
        </div>"""
    )


def test_navset_bar_markup():
    with private_seed_n():
        x = ui.navset_bar(
            ui.nav_menu("Menu", "Plain text", c),
            title="Page title",
            footer="Page footer",
            header="Page header",
        )

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <nav class="navbar navbar-expand-md navbar-default" data-bs-theme="auto">
          <div class="container-fluid">
            <span class="navbar-brand">Page title</span><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar-collapse-795772" aria-controls="navbar-collapse-795772" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
            <div id="navbar-collapse-795772" class="collapse navbar-collapse">
              <ul class="nav navbar-nav nav-underline" data-tabsetid="886440">
                <li class="nav-item dropdown">
                  <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
                  <ul class="dropdown-menu" data-tabsetid="404958">
                    <li class="dropdown-header">Plain text</li>
                    <li>
                      <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-404958-1">c</a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        </nav>
        <div class="container-fluid html-fill-item html-fill-container">
          Page header
          <div class="tab-content html-fill-item html-fill-container" data-tabsetid="886440">
            <div class="tab-pane active html-fill-item html-fill-container bslib-gap-spacing" role="tabpanel" data-value="c" id="tab-404958-1" style="--bslib-navbar-margin:0;;">c</div>
          </div>
          Page footer
        </div>"""
    )


# navbar_options() -------------------------------------------------------------------


def test_navbar_options_no_deprecated_arguments():
    options_user = navbar_options()
    result = navbar_options_resolve_deprecated(options_user)
    assert isinstance(result, NavbarOptions)
    assert result == navbar_options()


def test_navbar_options_deprecated_arguments():
    options_user = navbar_options()
    assert options_user._is_default.get("position", False)
    assert options_user._is_default.get("underline", False)

    with pytest.warns(ShinyDeprecationWarning, match="`position`, `underline`"):
        result = navbar_options_resolve_deprecated(
            options_user,
            position="static-top",
            underline=True,
        )

    assert isinstance(result, NavbarOptions)
    assert result == navbar_options()


def test_navbar_options_inverse_true():
    options_user = navbar_options()
    with pytest.warns(ShinyDeprecationWarning, match="`inverse`"):
        result = navbar_options_resolve_deprecated(options_user, inverse=True)
    assert isinstance(result, NavbarOptions)
    assert result.theme == "dark"


def test_navbar_options_inverse_false():
    options_user = navbar_options()
    with pytest.warns(ShinyDeprecationWarning, match="`inverse`"):
        result = navbar_options_resolve_deprecated(options_user, inverse=False)
    assert isinstance(result, NavbarOptions)
    assert result.theme == "light"


def test_navbar_options_inverse_invalid():
    options_user = navbar_options()
    with pytest.warns(ShinyDeprecationWarning, match="`inverse`"):
        with pytest.raises(ValueError, match="Invalid `inverse` value: 42"):
            navbar_options_resolve_deprecated(options_user, inverse=42)  # type: ignore


def test_navbar_options_conflicting_options():
    options_user = navbar_options(position="fixed-top")
    with pytest.warns(ShinyDeprecationWarning, match="`position`"):
        with pytest.warns(
            ShinyDeprecationWarning, match="`position` was provided twice"
        ):
            result = navbar_options_resolve_deprecated(
                options_user, position="fixed-bottom"
            )
    assert isinstance(result, NavbarOptions)
    assert result.position == "fixed-top"


def test_navbar_options_attribs_in_options_user():
    options_user = navbar_options(class_="my-navbar")
    result = navbar_options_resolve_deprecated(options_user)
    assert isinstance(result, NavbarOptions)
    assert result.attrs == {"class_": "my-navbar"}


def test_navbar_options_mixed_options():
    options_user = navbar_options(position="fixed-bottom", bg="light")
    assert not options_user._is_default.get("position", False)
    assert not options_user._is_default.get("bg", False)

    with pytest.warns(ShinyDeprecationWarning, match="`bg`"):
        with pytest.warns(ShinyDeprecationWarning, match="`bg` was provided twice"):
            result = navbar_options_resolve_deprecated(options_user, bg="dark")

    assert isinstance(result, NavbarOptions)
    assert result.position == "fixed-bottom"
    assert result.bg == "light"


def test_navbar_options_all_deprecated_arguments():
    options_user = navbar_options()
    with pytest.warns(
        ShinyDeprecationWarning,
        match="arguments of `navset_bar\\(\\)` for navbar options",
    ):
        result = navbar_options_resolve_deprecated(
            options_user,
            position="static-top",
            bg="dark",
            inverse=True,
            collapsible=True,
            underline=True,
        )
    assert isinstance(result, NavbarOptions)
    assert result.theme == "dark"


def test_navbar_options_fn_caller_custom():
    options_user = navbar_options()
    with pytest.warns(
        ShinyDeprecationWarning,
        match="arguments of `custom_caller\\(\\)` for navbar options",
    ):
        result = navbar_options_resolve_deprecated(
            options_user,
            position="static-top",
            fn_caller="custom_caller",
        )
    assert isinstance(result, NavbarOptions)
    assert result == navbar_options()
