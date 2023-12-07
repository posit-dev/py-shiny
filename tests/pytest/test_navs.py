"""Tests for """


import contextlib
import random
import textwrap
from typing import Generator

from htmltools import TagList

from shiny import ui
from shiny._utils import private_seed


# Fix the randomness of these functions to make the tests deterministic
@contextlib.contextmanager
def private_seed_n(n: int = 0) -> Generator[None, None, None]:
    with private_seed():
        random.seed(n)
        yield


def test_nav_markup():
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

    with private_seed_n():
        x = ui.navset_tab(a, b, ui.nav_control("Some item"), menu)

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

    with private_seed_n():
        x = ui.navset_pill(menu, a, id="navset_pill_id")

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
          <div class="card-body bslib-gap-spacing html-fill-item html-fill-container" style="margin-top:auto;margin-bottom:auto;flex:1 1 auto;">
            <div class="tab-content html-fill-item html-fill-container" data-tabsetid="7311">
              <div class="tab-pane html-fill-item html-fill-container" role="tabpanel" data-value="a" id="tab-7311-0" style="gap:0;padding:0;">a</div>
              <div class="tab-pane active html-fill-item html-fill-container" role="tabpanel" data-value="c" id="tab-7890-0" style="gap:0;padding:0;">c</div>
              <div class="tab-pane html-fill-item html-fill-container" role="tabpanel" data-value="b" id="tab-7311-2" style="gap:0;padding:0;">b</div>
            </div>
          </div>
          <script data-bslib-card-init="">window.bslib.Card.initializeAllCards();</script>
        </div>"""
    )

    with private_seed_n():
        x = ui.navset_bar(
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
        <div class="container-fluid html-fill-item html-fill-container">
          Page header
          <div class="tab-content html-fill-item html-fill-container" data-tabsetid="7311">
            <div class="tab-pane active html-fill-item html-fill-container" role="tabpanel" data-value="c" id="tab-7890-1" style="--bslib-navbar-margin:0;;">c</div>
          </div>
          Page footer
        </div>"""
    )
