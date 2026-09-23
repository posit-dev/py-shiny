from __future__ import annotations

import re

from shiny._docstring import html_escape_except_backticks
from shiny.ui import input_task_button

ENTITY_RE = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[a-zA-Z]+);")
CODE_SPAN_RE = re.compile(r"```.+?```|``.+?``|`[^`]*?`", flags=re.DOTALL)

# `html.escape()` (used by `html_escape_except_backticks`) only ever produces
# these entities. Outside of backtick code spans they are harmless (the browser
# renders them as the original characters), so they form the allowlist for the
# escaped text. Inside code spans, no entity is ever expected: an entity there
# means a literal (e.g. `"`) was escaped and will render as `&quot;` in the
# final docs page instead of `"`.
# See https://github.com/posit-dev/py-shiny/issues/2502.
ALLOWED_ESCAPES_OUTSIDE_CODE = frozenset({"&amp;", "&lt;", "&gt;", "&quot;", "&#x27;"})


def _entities_outside_code(s: str) -> list[str]:
    without_code = CODE_SPAN_RE.sub("", s)
    return ENTITY_RE.findall(without_code)


def _entities_inside_code(s: str) -> list[str]:
    entities: list[str] = []
    for match in CODE_SPAN_RE.finditer(s):
        entities.extend(ENTITY_RE.findall(match.group(0)))
    return entities


def test_escape_preserves_single_backtick_spans():
    rendered = html_escape_except_backticks('a `code "hi" <b>there</b>` b')
    assert rendered == 'a `code "hi" <b>there</b>` b'


def test_escape_preserves_double_backtick_spans():
    # Regression test for https://github.com/posit-dev/py-shiny/issues/2502:
    # RST-style ``literals`` containing quotes must not be escaped to `&quot;`.
    rendered = html_escape_except_backticks(
        'calling ``update_task_button(id, state="ready")`` after'
    )
    assert rendered == 'calling ``update_task_button(id, state="ready")`` after'
    assert "&quot;" not in rendered


def test_escape_escapes_html_outside_code():
    rendered = html_escape_except_backticks("a <b>hi</b> b `code <i>x</i>`")
    assert rendered == "a &lt;b&gt;hi&lt;/b&gt; b `code <i>x</i>`"


def test_input_task_button_docs_have_no_unexpected_escaping():
    rendered = html_escape_except_backticks(input_task_button.__doc__ or "")

    inside = _entities_inside_code(rendered)
    assert inside == [], (
        f"Unexpected HTML entities inside code spans: {inside}. "
        'Literals like ``state="ready"`` must render with plain quotes.'
    )

    outside = _entities_outside_code(rendered)
    unexpected = [e for e in outside if e not in ALLOWED_ESCAPES_OUTSIDE_CODE]
    assert (
        unexpected == []
    ), f"Unexpected HTML entities outside code spans: {unexpected}"


def test_input_task_button_docstring_uses_plain_func_roles():
    # `:func:` roles with call arguments (e.g.
    # `:func:`~shiny.ui.update_task_button(id, state="busy")``) are not
    # converted to links by quartodoc and leak a literal ":func:" prefix onto
    # the rendered page.
    doc = input_task_button.__doc__ or ""
    bad_roles = re.findall(r":func:`[^`]*\([^`]*`", doc)
    assert bad_roles == [], f"Docstring has :func: roles with arguments: {bad_roles}"
