import re

from e2e.controls import attr_match_str, style_match_str, xpath_match_str


def test_style_match_str() -> None:
    reg = style_match_str("key", "value")

    def has_match(x: str):
        return reg.search(x) is not None

    def no_match(x: str):
        return reg.search(x) is None

    assert has_match("key: value;")
    assert has_match("key:value")
    assert has_match("key:value;")
    assert has_match(" key : value ; ")

    assert no_match("key:value-bar")
    assert no_match("key:value-bar;")
    assert no_match(" key : value-bar ; ")

    assert no_match("otherkey:value")
    assert no_match("otherkey:value;")
    assert no_match(" otherkey : value ; ")


def test_attr_match_str() -> None:
    assert attr_match_str("key", "value") == 'key="value"'
    assert attr_match_str("key", 'value"value2') == r'key="value\"value2"'


def test_xpath_match_str() -> None:
    assert xpath_match_str("key", "value") == '@key="value"'
    assert xpath_match_str("key", 'value"value2') == r'@key="value\"value2"'

    assert xpath_match_str("key", re.compile("value")) == 'matches(@key, "value")'
    assert (
        xpath_match_str("key", re.compile(r"\bvalue\b"))
        == r'matches(@key, "\bvalue\b")'
    )
