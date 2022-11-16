"""Barret Facade classes for working with Shiny inputs/outputs in Playwright"""

# pyright: reportUnknownMemberType=false

import typing

from playwright.sync_api import Locator, Page
from playwright.sync_api import expect as playwright_expect

AttrValue = str | typing.Pattern[str]
Timeout = float | None


def assert_el_has_class(loc: Locator, cls: str):
    el_cls = loc.get_attribute("class")
    if el_cls is None:
        raise AssertionError("Element has no class attribute")
    assert el_cls.index(cls) >= 0


def float_attr(loc: Locator, key: str, timeout: Timeout = None) -> (float | None):
    ret = loc.get_attribute(key, timeout=timeout)
    if ret is not None:
        ret = float(ret)
    return ret


def expect_attr(
    loc: Locator, attr_name: str, value: AttrValue | None, timeout: Timeout = None
):
    """Expect an attribute to have a value. If `value` is `None`, then an immediate assertion is made on the attribute's existence."""
    if type(value) is None:
        has_attr = loc.evaluate(
            f"el => el.hasAttribute('{attr_name}')", timeout=timeout
        )
        assert has_attr, f"Element does not have attribute {attr_name}"
        return

    value = typing.cast(AttrValue, value)
    playwright_expect(loc).to_have_attribute(attr_name, value, timeout=timeout)


class SimpleRootInput:
    # timeout: Timeout
    id: str
    container: Locator
    loc: Locator

    def __init__(
        self,
        page: Page,
        *,
        id: str,
        container: str,
        loc: str,
    ):
        self.page = page
        # Needed?!? This is covered by `self.loc_root` and possibly `self.loc`
        self.id = id
        self.container = page.locator(container).filter(has=page.locator(loc))
        self.loc = self.container.locator(loc)
        # self.timeout = timeout

    @property
    def expect(self):
        return playwright_expect(self.loc)

    ## Requires a PR to playwright to call `obj.__expect__()` method; Desired API
    # def __expect__(self) -> LocatorAssertions:
    #     return playwright_expect(self.loc)


# Class definitions
# * Fields
#   * Try to mirror playwright as much as possible.
#   * There are no properties, only methods; This allows for timeout values to be passed through and for complex methods.
#     * Locators will stay as properties
#   * Don't sub-class. For now, use `_` separatation and use `loc` or `value` as a prefix
# * Approach
#   * Use locators / playwright_expect as much as possible
#     * It should not be necessary to use `assert` directly.
#     * MUST wait for `Locator`s to do their job
#   * Provide `value` methods as a convenience


class NumericInputDos(SimpleRootInput):
    # id: str,
    # label: TagChildArg,
    # value: float,
    # *,
    # min: Optional[float] = None,
    # max: Optional[float] = None,
    # step: Optional[float] = None,
    # width: Optional[str] = None,
    def __init__(self, page: Page, id: str, *, verify: bool = True):
        super().__init__(
            page,
            id=id,
            # container="../",
            container="div.shiny-input-container",
            loc=f"input#{id}[type=number].shiny-bound-input",
        )

        self.loc_label = self.container.locator("label")

        # Must be last
        if verify:
            self.verify()

    def verify(self):
        assert_el_has_class(self.loc, "form-control")
        type_attr = self.loc.get_attribute("type")
        if type_attr is None:
            raise AssertionError("Element has no 'type' attribute")
        assert type_attr == "number"

        assert_el_has_class(self.container, "form-group")
        assert_el_has_class(self.container, "shiny-input-container")

    def set(self, value: float, *, timeout: Timeout = None):
        self.loc.fill(str(value), timeout=timeout)

    def value(self, *, timeout: Timeout = None) -> float:
        self.loc_label

        # Should we use jquery?
        # return self.locations["label"].evaluate("el => $(el).val()", timeout=timeout)

        # # TODO int or float depending on step size?
        # step_val = step_fn(timeout)

        # conv_method = int
        # if step_val is None or not step_val.is_integer():
        #     conv_method = float
        # value = self.loc.input_value()
        # return conv_method(value)

        return float(self.loc.input_value(timeout=timeout))

    def value_label(self, *, timeout: Timeout = None) -> (str | None):
        return self.loc_label.text_content(timeout=timeout)

    def value_min(self, *, timeout: Timeout = None) -> (float | None):
        return float_attr(self.loc, "min", timeout=timeout)

    def value_max(self, *, timeout: Timeout = None) -> (float | None):
        return float_attr(self.loc, "max", timeout=timeout)

    def value_step(self, *, timeout: Timeout = None) -> (float | None):
        return float_attr(self.loc, "step", timeout=timeout)

    def value_width(self, *, timeout: Timeout = None) -> (float | None):
        return float_attr(self.loc, "width", timeout=timeout)

    def expect_label_to_have_text(self, value: str, *, timeout: Timeout = None):
        playwright_expect(self.loc_label).to_have_text(value, timeout=timeout)

    def expect_min_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        assert type(value) is not None
        expect_attr(self.loc, "min", value=value, timeout=timeout)

    def expect_max_to_have_value(self, value: AttrValue, *, timeout: Timeout = None):
        assert type(value) is not None
        expect_attr(self.loc, "max", value=value, timeout=timeout)

    def expect_step_to_have_value(
        self, value: AttrValue | None, *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "step", value=value, timeout=timeout)

    def expect_width_to_have_value(
        self, value: AttrValue | None, *, timeout: Timeout = None
    ):
        expect_attr(self.loc, "width", value=value, timeout=timeout)
