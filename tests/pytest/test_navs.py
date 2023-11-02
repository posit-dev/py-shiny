"""Tests for """


import random
import textwrap
from typing import Any, Callable

from htmltools import TagList

from shiny import ui
from shiny._utils import private_seed
from shiny.ui._navs import NavSet


# Fix the randomness of these functions to make the tests deterministic
def with_private_seed(func: Callable[[], NavSet], *args: Any, **kwargs: Any):
    with private_seed():
        random.seed(0)
        return func(*args, **kwargs)


def test_nav_markup():
    a = ui.nav("a", "a")
    b = ui.nav("b", "b")
    c = ui.nav("c", "c")
    menu = ui.nav_menu(
        "Menu",
        c,
        "----",
        "Plain text",
        "----",
        ui.nav_control("Other item"),
    )

    x = with_private_seed(ui.navset_tab, a, b, ui.nav_control("Some item"), menu)

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <ul class="nav nav-tabs" data-tabsetid="7311">
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link active" href="#tab-7311-0">a</a>
          </li>
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="b" role="tab" class="nav-link" href="#tab-7311-1">b</a>
          </li>
          <li>Some item</li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle " data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
            <ul class="dropdown-menu" data-tabsetid="7890">
              <li>
                <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item" href="#tab-7890-0">c</a>
              </li>
              <li class="dropdown-divider"></li>
              <li class="dropdown-header">Plain text</li>
              <li class="dropdown-divider"></li>
              <li>Other item</li>
            </ul>
          </li>
        </ul>
        <div class="tab-content" data-tabsetid="7311">
          <div class="tab-pane active" role="tabpanel" data-value="a" id="tab-7311-0">a</div>
          <div class="tab-pane" role="tabpanel" data-value="b" id="tab-7311-1">b</div>
          <div class="tab-pane" role="tabpanel" data-value="c" id="tab-7890-0">c</div>
        </div>"""
    )

    x = with_private_seed(
        ui.navset_pill,
        menu,
        a,
        id="navset_pill_id",
    )

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <ul class="nav nav-pills shiny-tab-input" id="navset_pill_id" data-tabsetid="7311">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
            <ul class="dropdown-menu" data-tabsetid="7890">
              <li>
                <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-7890-0">c</a>
              </li>
              <li class="dropdown-divider"></li>
              <li class="dropdown-header">Plain text</li>
              <li class="dropdown-divider"></li>
              <li>Other item</li>
            </ul>
          </li>
          <li class="nav-item">
            <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link" href="#tab-7311-1">a</a>
          </li>
        </ul>
        <div class="tab-content" data-tabsetid="7311">
          <div class="tab-pane active" role="tabpanel" data-value="c" id="tab-7890-0">c</div>
          <div class="tab-pane" role="tabpanel" data-value="a" id="tab-7311-1">a</div>
        </div>"""
    )

    x = with_private_seed(
        ui.navset_card_pill,
        a,
        ui.nav_menu("Menu", c),
        b,
        selected="c",
    )

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <div class="html-fill-container html-fill-item card bslib-card bslib-mb-spacing" data-bslib-card-init="">
          <div class="card-header">
            <ul class="nav nav-pills card-header-pills" data-tabsetid="7311">
              <li class="nav-item">
                <a data-bs-toggle="tab" data-toggle="tab" data-value="a" role="tab" class="nav-link" href="#tab-7311-0">a</a>
              </li>
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
                <ul class="dropdown-menu" data-tabsetid="7890">
                  <li>
                    <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-7890-0">c</a>
                  </li>
                </ul>
              </li>
              <li class="nav-item">
                <a data-bs-toggle="tab" data-toggle="tab" data-value="b" role="tab" class="nav-link" href="#tab-7311-2">b</a>
              </li>
            </ul>
          </div>
          <div class="html-fill-container html-fill-item card-body bslib-gap-spacing" style="margin-top:auto;margin-bottom:auto;flex:1 1 auto;">
            <div class="html-fill-container html-fill-item tab-content" data-tabsetid="7311">
              <div class="html-fill-container html-fill-item tab-pane" role="tabpanel" data-value="a" id="tab-7311-0" style="gap:0;padding:0;">a</div>
              <div class="html-fill-container html-fill-item tab-pane active" role="tabpanel" data-value="c" id="tab-7890-0" style="gap:0;padding:0;">c</div>
              <div class="html-fill-container html-fill-item tab-pane" role="tabpanel" data-value="b" id="tab-7311-2" style="gap:0;padding:0;">b</div>
            </div>
          </div>
          <script data-bslib-card-init="">window.bslib.Card.initializeAllCards();</script>
        </div>"""
    )

    x = with_private_seed(
        ui.navset_bar,  # type: ignore
        ui.nav_menu("Menu", "Plain text", c),
        title="Page title",
        footer="Page footer",
        header="Page header",
    )

    assert TagList(x).render()["html"] == textwrap.dedent(
        """\
        <nav class="navbar navbar-expand-md navbar-light bg-light">
          <div class="container-fluid">
            <span class="navbar-brand">Page title</span><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar-collapse-1663" aria-controls="navbar-collapse-1663" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button>
            <div id="navbar-collapse-1663" class="collapse navbar-collapse">
              <ul class="nav navbar-nav nav-underline" data-tabsetid="7311">
                <li class="nav-item dropdown">
                  <a class="nav-link dropdown-toggle active" data-bs-toggle="dropdown" data-value="Menu" href="#" role="button">Menu</a>
                  <ul class="dropdown-menu" data-tabsetid="7890">
                    <li class="dropdown-header">Plain text</li>
                    <li>
                      <a data-bs-toggle="tab" data-toggle="tab" data-value="c" role="tab" class="dropdown-item active" href="#tab-7890-1">c</a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        </nav>
        <div class="html-fill-container html-fill-item container-fluid">
          Page header
          <div class="html-fill-container html-fill-item tab-content" data-tabsetid="7311">
            <div class="html-fill-container html-fill-item tab-pane active" role="tabpanel" data-value="c" id="tab-7890-1" style="--bslib-navbar-margin:0;;">c</div>
          </div>
          Page footer
        </div>"""
    )
