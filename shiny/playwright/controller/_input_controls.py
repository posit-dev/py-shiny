from __future__ import annotations

import time
import typing

from playwright.sync_api import FloatRect, Locator, Page
from playwright.sync_api import expect as playwright_expect

from ...types import MISSING, MISSING_TYPE, ListOrTuple
from .._types import AttrValue, ListPatternOrStr, PatternOrStr, Timeout
from ..expect._expect import _attr_match_str
from ..expect._internal import (
    expect_attribute_to_have_value as _expect_attribute_to_have_value,
)
from ..expect._internal import expect_class_to_have_value as _expect_class_to_have_value
from ..expect._internal import expect_style_to_have_value as _expect_style_to_have_value
from ._base import (
    InitLocator,
    UiWithLabel,
    WidthContainerStyleM,
    all_missing,
    not_is_missing,
)
from ._expect import (
    expect_locator_contains_values_in_list,
    expect_locator_values_in_list,
)


class _InputSliderBase(
    WidthContainerStyleM,
    UiWithLabel,
):

    loc_irs: Locator
    """
    Playwright `Locator` of the input slider.
    """
    loc_irs_ticks: Locator
    """
    Playwright `Locator` of the input slider ticks.
    """
    loc_play_pause: Locator
    """
    Playwright `Locator` of the play/pause button.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSlider.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the slider.
        """
        super().__init__(
            page,
            id=id,
            loc=f"input#{id}",
        )
        self.loc_irs = self.loc_container.locator("> .irs.irs--shiny")
        self.loc_irs_ticks = self.loc_irs.locator("> .irs-grid > .irs-grid-text")
        self.loc_play_pause = self.loc_container.locator(
            "> .slider-animate-container a"
        )

    def expect_tick_labels(
        self,
        value: ListPatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the tick labels of the input slider.

        Parameters
        ----------
        value
            The expected tick labels.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if value is None:
            playwright_expect(self.loc_irs_ticks).to_have_count(0)
            return

        playwright_expect(self.loc_irs_ticks).to_have_text(value, timeout=timeout)

    def expect_animate(self, exists: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the animate button to exist.

        Parameters
        ----------
        exists
            Whether the animate button should exist.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        animate_count = 1 if exists else 0
        playwright_expect(self.loc_play_pause).to_have_count(animate_count)

    # This method doesn't feel like it should accept text as the user does not control the value
    # They only control either `True` or `False`
    def expect_animate_options(
        self,
        *,
        loop: bool | MISSING_TYPE = MISSING,
        interval: float | MISSING_TYPE = MISSING,
        timeout: Timeout = None,
    ) -> None:
        if all_missing(loop, interval):
            raise ValueError("Must provide at least one of `loop` or `interval`")
        # TODO-future; Composable expectations
        self.expect_animate(exists=True, timeout=timeout)
        if not_is_missing(loop):
            _expect_attribute_to_have_value(
                self.loc_play_pause,
                "data-loop",
                "" if loop else None,
                timeout=timeout,
            )
        if not_is_missing(interval):
            _expect_attribute_to_have_value(
                self.loc_play_pause,
                "data-interval",
                str(interval),
                timeout=timeout,
            )

    # No `toggle` method as short animations with no loops can cause the button to
    # become `play` over and over again. Instead, have explicit `play` and `pause`
    # methods.
    def click_play(self, *, timeout: Timeout = None) -> None:
        """
        Click the play button.

        Parameters
        ----------
        timeout
            The timeout for the action. Defaults to `None`.
        """
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_to_have_value(
            self.loc_play_pause,
            "playing",
            has_class=False,
            timeout=timeout,
        )
        self.loc_play_pause.click()

    def click_pause(self, *, timeout: Timeout = None) -> None:
        """
        Click the pause button.

        Parameters
        ----------
        timeout
            The timeout for the action. Defaults to `None`.
        """
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        _expect_class_to_have_value(
            self.loc_play_pause, "playing", has_class=True, timeout=timeout
        )
        self.loc_play_pause.click()

    def expect_min(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `min` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-min", value=value, timeout=timeout
        )

    def expect_max(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `max` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-max", value=value, timeout=timeout
        )

    def expect_step(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `step` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-step", value=value, timeout=timeout
        )

    def expect_ticks(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-ticks` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-grid", value=value, timeout=timeout
        )

    def expect_sep(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-sep` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-prettify-separator", value=value, timeout=timeout
        )

    def expect_pre(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-pre` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-prefix", value=value, timeout=timeout
        )

    def expect_post(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the input element to have the expected `data-post` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-postfix", value=value, timeout=timeout
        )

    # def expect_data_type(
    #     self, value: AttrValue, *, timeout: Timeout = None
    # ) -> None:
    #     expect_attr(self.loc, "data-data-type", value=value, timeout=timeout)

    def expect_time_format(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-time-format` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-time-format", value=value, timeout=timeout
        )

    def expect_timezone(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-timezone` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-timezone", value=value, timeout=timeout
        )

    def expect_drag_range(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected `data-drag-range` attribute value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc, "data-drag-interval", value=value, timeout=timeout
        )

    def _wait_for_container(self, *, timeout: Timeout = None) -> None:
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)

    # JS expression computing the slider's step positions and where the given
    # handle sits among them, from ionRangeSlider's internal state (which updates
    # synchronously on every interaction, unlike the throttled label repaints).
    # `labels` mirrors what `drawLabels()` renders at each step position; `cur`
    # is the handle's current position index; `lo`/`hi` are the position indices
    # the handle can reach (a range slider handle is bounded by its sibling).
    _SLIDER_STEP_STATE_JS = """(el, resultKey) => {
        const inst = window.jQuery(el).data("ionRangeSlider");
        const opts = inst.options;
        const hasValues = opts.values.length > 0;
        const labelFor = (val) =>
            hasValues
                ? String(inst.decorate(opts.p_values[val]))
                : String(inst.decorate(inst._prettify(val), val));
        const labels = [];
        const stepValues = [];
        for (let k = 0; opts.step > 0 && k <= 100000; k++) {
            let val = inst.toFixed(opts.min + k * opts.step);
            if (val >= opts.max) {
                val = opts.max;
            }
            labels.push(labelFor(val));
            stepValues.push(val);
            if (val === opts.max) {
                break;
            }
        }
        const idxOf = (val) => {
            let best = 0;
            for (let k = 0; k < stepValues.length; k++) {
                if (Math.abs(stepValues[k] - val) < Math.abs(stepValues[best] - val)) {
                    best = k;
                }
            }
            return best;
        };
        const cur = idxOf(inst.result[resultKey]);
        const lo = resultKey === "to" ? idxOf(inst.result.from) : 0;
        const hi =
            resultKey === "from" && opts.type === "double"
                ? idxOf(inst.result.to)
                : labels.length - 1;
        return { labels: labels, cur: cur, lo: lo, hi: hi };
    }"""

    def _set_helper(
        self,
        *,
        value: str,
        irs_label: Locator,
        handle: Locator,
        max_err_values: int = 15,
    ) -> None:
        """
        Drag the slider `handle` directly to the position of the `value` label.

        The label text at every step position is computed from the widget's
        internal state (the label element repaints on a throttled animation frame
        loop and cannot be reliably sampled mid-drag), the target position is
        located in that list, and the handle is dragged straight to that
        position's pixel coordinate. Only the final mouse position matters, so
        coalesced or dropped mouse-move events cannot skip the target; the result
        is verified against the widget's internal state and the drag is retried
        if it did not land.

        Parameters
        ----------
        value
            The value to set the slider to.
        irs_label
            Playwright `Locator` of the slider handle's value label.
        handle
            Playwright `Locator` of the slider handle to move.
        max_err_values
            The maximum number of error values to display if the value is not found.
        """
        # Which `result` entry tracks this handle ("from" for single sliders and
        # `from` handles, "to" for `to` handles)
        handle_class = handle.get_attribute("class") or ""
        result_key = "to" if "to" in handle_class.split() else "from"

        def read_step_state() -> typing.Tuple[typing.List[str], int, int, int]:
            state = self.loc.evaluate(self._SLIDER_STEP_STATE_JS, result_key)
            return (
                [str(label) for label in state["labels"]],
                int(state["cur"]),
                int(state["lo"]),
                int(state["hi"]),
            )

        def read_settled_position() -> int:
            # Input events are processed asynchronously by the browser, so a
            # state read can overtake in-flight events; poll until the position
            # holds steady across consecutive reads
            _, pos, _, _ = read_step_state()
            for _ in range(20):
                time.sleep(0.05)
                _, next_pos, _, _ = read_step_state()
                if next_pos == pos:
                    return pos
                pos = next_pos
            return pos

        labels, cur, lo, hi = read_step_state()

        if value not in labels:
            display_labels = labels[:max_err_values]
            trail_txt = ""
            if len(labels) > max_err_values:
                trail_txt = f", ...\nTo display more values, increase `set(max_err_values={max_err_values})`"
            values_found_txt = ", ".join([f'"{label}"' for label in display_labels])
            raise ValueError(
                f"Could not find value '{value}' among the slider's values\n"
                + f"Values found:\n{values_found_txt}{trail_txt}"
            )
        target = labels.index(value)
        if not (lo <= target <= hi):
            raise ValueError(
                f"Value '{value}' is not reachable by this slider handle; "
                + "the other handle currently limits it to values from "
                + f"'{labels[lo]}' to '{labels[hi]}'"
            )

        n_steps = len(labels) - 1
        if n_steps == 0:
            playwright_expect(irs_label).to_have_text(value)
            return

        mouse = self.loc_container.page.mouse
        grid_bb = self._grid_bb()
        for _ in range(3):
            if cur == target:
                break
            handle_bb = handle.bounding_box()
            if handle_bb is None:
                raise RuntimeError("Couldn't find bounding box for the slider handle")
            handle_w = handle_bb["width"]
            y = handle_bb["y"] + handle_bb["height"] / 2
            # The handle's center travels from `grid left + half handle width`
            # (first position) to `grid right - half handle width` (last position)
            target_x = (
                grid_bb["x"]
                + handle_w / 2
                + (grid_bb["width"] - handle_w) * (target / n_steps)
            )
            mouse.move(handle_bb["x"] + handle_w / 2, y)
            mouse.down()
            mouse.move(target_x, y, steps=5)
            # Re-send the final position so it lands even if the browser dropped
            # or coalesced the earlier moves
            time.sleep(0.05)
            mouse.move(target_x, y)
            mouse.up()
            cur = read_settled_position()

        if cur != target:
            # Mouse coordinates are quantized to whole pixels, so when a slider
            # has more steps than the track has pixels, the drag can land a step
            # or two off a target that no integer pixel maps to. Finish with
            # arrow keys, which move the handle by exactly one step per press.
            line = self.loc_irs.locator("> .irs > .irs-line")
            # Click the handle so ionRangeSlider targets it for keyboard input
            # and aligns its internal pointer with the handle; a residual pointer
            # offset from the drag would silently absorb key presses
            handle.click()
            cur = read_settled_position()
            for _ in range(30):
                if cur == target:
                    break
                line.press("ArrowRight" if target > cur else "ArrowLeft")
                cur = read_settled_position()

        if cur != target:
            raise ValueError(
                f"Could not drag the slider handle to value '{value}'; "
                + f"it landed on '{labels[cur]}' instead"
            )

        # Wait for the throttled label repaint to reflect the final position
        playwright_expect(irs_label).to_have_text(value)

    def _grid_bb(self, *, timeout: Timeout = None) -> FloatRect:
        grid = self.loc_irs.locator("> .irs > .irs-line")
        grid_bb = grid.bounding_box(timeout=timeout)
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-line")
        return grid_bb


class _RadioButtonCheckboxGroupBase(
    WidthContainerStyleM,
    UiWithLabel,
):
    loc_choice_labels: Locator

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the labels of the choices.

        Parameters
        ----------
        value
            The expected labels.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        if len(value) == 1:
            labels_val = value[0]
        else:
            labels_val = value
        playwright_expect(self.loc_choice_labels).to_have_text(
            labels_val,
            timeout=timeout,
        )

    def expect_inline(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input to be inline.

        Parameters
        ----------
        value
            Whether the input is inline.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        _expect_class_to_have_value(
            self.loc_container,
            "shiny-input-container-inline",
            has_class=value,
            timeout=timeout,
        )


class InputRadioButtons(
    _RadioButtonCheckboxGroupBase,
):
    """Controller for :func:`shiny.ui.input_radio_buttons`."""

    loc_selected: Locator
    """
    Playwright `Locator` of the selected radio button.
    """
    loc_choices: Locator
    """
    Playwright `Locator` of the radio button choices.
    """
    loc_choice_labels: Locator
    """
    Playwright `Locator` of the labels of the radio button choices.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """Initialize the InputRadioButtons.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the radio buttons.
        """
        super().__init__(
            page,
            id=id,
            # Similar to `select` tag in `InputSelect`'s `loc`
            # loc should be the `.shiny-bound-input` element
            # This happens to be the container
            loc="xpath=.",
            loc_container=f"div#{id}.shiny-input-radiogroup.shiny-bound-input",
        )

        # # Regular example
        #     <div class="shiny-options-group">
        #       <div class="radio">
        #         <label>
        #           <input type="radio" name="radio1" value="a" checked="checked">
        #           <span><span style="color:red;">A</span></span>
        # # Inline example
        #     <div class="shiny-options-group">
        #       <label class="radio-inline">
        #         <input type="radio" name="radio2" value="d" checked="checked">
        #         <span><span style="color:purple;">D</span></span>
        input_radio = f"> .shiny-options-group input[type=radio][name={id}]"
        self.loc_selected = self.loc.locator(f"{input_radio}:checked")
        self.loc_choices = self.loc.locator(f"{input_radio}")
        # Get sibling <span> containing the label text
        self.loc_choice_labels = self.loc.locator(f"{input_radio} + span")

    def set(
        self,
        selected: str,
        *,
        timeout: Timeout = None,
        **kwargs: object,
    ) -> None:
        """
        Set the selected radio button.

        Parameters
        ----------
        selected
            The value of the selected radio button.
        timeout
            The timeout for the action. Defaults to `None`.
        """
        if not isinstance(selected, str):
            raise TypeError("`selected=` must be a string")

        # Only need to set.
        # The Browser will _unset_ the previously selected radio button
        self.loc_container.locator(
            f"label input[type=radio][{_attr_match_str('value', selected)}]"
        ).check(timeout=timeout)

    def expect_choices(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the radio button choices.

        Parameters
        ----------
        value
            The expected choices.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=radio]",
            arr_name="choices",
            arr=value,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: PatternOrStr | None,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected radio button.

        Parameters
        ----------
        value
            The expected value of the selected radio button.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if value is None:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_selected).to_have_value(value, timeout=timeout)


class _InputCheckboxBase(
    WidthContainerStyleM,
    UiWithLabel,
):
    def __init__(
        self, page: Page, id: str, loc: InitLocator, loc_label: str | None
    ) -> None:
        """
        Initializes the input checkbox.

        Parameters
        ----------
        page
            The page where the input checkbox is located.
        id
            The id of the input checkbox.
        loc
            Playwright `Locator` of the input checkbox.
        loc_label
            Playwright `Locator` of the label of the input checkbox.
        """
        super().__init__(
            page,
            id=id,
            loc=loc,
            loc_label=loc_label,
        )

    def set(self, value: bool, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Sets the input checkbox.

        Parameters
        ----------
        value
            The value of the input checkbox.
        timeout
            The maximum time to wait for the input checkbox to be set. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.set_checked(
            value, timeout=timeout, **kwargs  # pyright: ignore[reportArgumentType]
        )

    def _toggle(self, *, timeout: Timeout = None, **kwargs: object) -> None:
        """
        Toggles the input checkbox.

        Parameters
        ----------
        timeout
            The maximum time to wait for the input checkbox to be toggled. Defaults to `None`.
        """
        self.loc.wait_for(state="visible", timeout=timeout)
        self.loc.scroll_into_view_if_needed(timeout=timeout)
        self.loc.click(timeout=timeout, **kwargs)  # pyright: ignore[reportArgumentType]

    def expect_checked(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input checkbox to be checked.

        Parameters
        ----------
        value
            Whether the input checkbox is checked.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value:
            self.expect.to_be_checked(timeout=timeout)
        else:
            self.expect.not_to_be_checked(timeout=timeout)


class InputCheckboxGroup(
    _RadioButtonCheckboxGroupBase,
):
    """Controller for :func:`shiny.ui.input_checkbox_group`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputCheckboxGroup.

        Parameters
        ----------
        page
            Playwright `Page` of the Shiny app.
        id
            The id of the checkbox group.
        """
        super().__init__(
            page,
            id=id,
            # Similar to `select` tag in `InputSelect`'s `loc`
            # loc should be the `.shiny-bound-input` element
            # This happens to be the container
            loc="xpath=.",
            loc_container=f"div#{id}.shiny-input-checkboxgroup.shiny-bound-input",
        )

        # # Regular example
        #     <div class="shiny-options-group">
        #       <div class="checkbox">
        #         <label>
        #           <input type="checkbox" name="check1" value="red">
        #           <span><span style="color: #FF0000;">RED</span></span>
        # # Inline example
        #     <div class="shiny-options-group">
        #       <label class="checkbox-inline">
        #         <input type="checkbox" name="check2" value="magenta">
        #         <span><span style="color: #FF00AA;">MAGENTA</span></span>
        input_checkbox = f"> .shiny-options-group input[type=checkbox][name={id}]"
        self.loc_selected = self.loc.locator(f"{input_checkbox}:checked")
        self.loc_choices = self.loc.locator(f"{input_checkbox}")
        # Get sibling <span> containing the label text
        self.loc_choice_labels = self.loc.locator(f"{input_checkbox} + span")

    def set(
        self,
        # TODO-future: Allow `selected` to be a single Pattern to perform matching against many items
        selected: ListOrTuple[str],
        *,
        timeout: Timeout = None,
        **kwargs: object,
    ) -> None:
        """
        Set the selected checkboxes.

        Parameters
        ----------
        selected
            The values of the selected checkboxes.
        timeout
            The timeout for the action. Defaults to `None`.
        """
        # Having an arr of size 0 is allowed. Will uncheck everything
        if not isinstance(selected, list):
            raise TypeError("`selected=` must be a list or tuple")
        for item in selected:
            if not isinstance(item, str):
                raise TypeError("`selected=` must be a list of strings")

        # Make sure the selected items exist
        # Similar to `self.expect_choices(choices = selected)`, but with
        # `is_exact=False` to allow for values not in `selected`.
        expect_locator_contains_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="selected",
            arr=selected,
            timeout=timeout,
        )

        def in_selected(value: str) -> bool:
            for item in selected:
                if isinstance(item, str):
                    if item == value:
                        return True
                elif isinstance(item, typing.Pattern):
                    if item.search(value):
                        return True
            return False

        for i in range(self.loc_choices.count()):
            checkbox = self.loc_choices.nth(i)
            is_selected = in_selected(checkbox.input_value(timeout=timeout))
            currently_selected = checkbox.is_checked()
            # Only update if needed
            if is_selected != currently_selected:
                checkbox.set_checked(
                    is_selected,
                    timeout=timeout,
                    **kwargs,  # pyright: ignore[reportArgumentType]
                )

    def expect_choices(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the checkbox choices.

        Parameters
        ----------
        value
            The expected choices.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="choices",
            arr=value,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected checkboxes.

        Parameters
        ----------
        value
            The expected values of the selected checkboxes.
        timeout
            The timeout for the expectation. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="input[type=checkbox]",
            arr_name="selected",
            arr=value,
            timeout=timeout,
            is_checked=True,
        )


class InputCheckbox(_InputCheckboxBase):
    """Controller for :func:`shiny.ui.input_checkbox`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input checkbox.

        Parameters
        ----------
        page
            The page where the input checkbox is located.
        id
            The id of the input checkbox.
        """
        super().__init__(
            page,
            id=id,
            loc=f"div.checkbox > label > input#{id}[type=checkbox].shiny-bound-input",
            loc_label="label > span",
        )


class InputSwitch(_InputCheckboxBase):
    """Controller for :func:`shiny.ui.input_switch`."""

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initializes the input switch.

        Parameters
        ----------
        page
            The page where the input switch is located.
        id
            The id of the input switch.
        """
        super().__init__(
            page,
            id=id,
            loc=f"div.form-switch > input#{id}[type=checkbox].shiny-bound-input",
            loc_label=f"label[for={id}]",
        )


class InputSelect(
    WidthContainerStyleM,
    UiWithLabel,
):
    """
    Controller for :func:`shiny.ui.input_select`.

    If you have defined your app's select input (`ui.input_select()`) with `selectize=TRUE`, use `InputSelectize` to test your app's UI.
    """

    def __init__(self, page: Page, id: str) -> None:
        """
        Initializes the input select.

        Parameters
        ----------
        page
            The page where the input select is located.
        id
            The id of the input select.
        """
        super().__init__(
            page,
            id=id,
            loc=f"select#{id}.shiny-bound-input.form-select",
        )
        self.loc_selected = self.loc.locator("option:checked")
        self.loc_choices = self.loc.locator("option")
        self.loc_choice_groups = self.loc.locator("optgroup")

    def set(
        self,
        selected: str | ListOrTuple[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the selected option(s) of the input select.

        Parameters
        ----------
        selected
            The value(s) of the selected option(s).
        timeout
            The maximum time to wait for the selection to be set. Defaults to `None`.
        """
        if isinstance(selected, str):
            selected = [selected]
        self.loc.select_option(value=selected, timeout=timeout)

    # If `selectize=` parameter does not become deprecated, uncomment this
    # # selectize: bool = False,
    # def expect_selectize(self, value: bool, *, timeout: Timeout = None) -> None:
    #     """
    #     Expect the input select to be selectize.

    #     Parameters
    #     ----------
    #     value
    #         Whether the input select is selectize.
    #     timeout
    #         The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
    #     """
    #     # class_=None if selectize else "form-select",
    #     _expect_class_to_have_value(
    #         self.loc,
    #         "form-select",
    #         has_class=not value,
    #         timeout=timeout,
    #     )

    def expect_choices(
        self,
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the available options of the input select to be an exact match.

        Parameters
        ----------
        choices
            The expected choices of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        # Playwright doesn't like lists of size 0. Instead, check for empty locator
        if len(choices) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="option",
            arr_name="choices",
            arr=choices,
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: PatternOrStr | ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected option(s) of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected value(s) of the selected option(s).
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if isinstance(value, list) and len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        if isinstance(value, list):
            self.expect.to_have_values(value, timeout=timeout)
        else:
            self.expect.to_have_value(value, timeout=timeout)

        # expect_locator_values_in_list(
        #     page=self.page,
        #     loc_container=self.loc_container,
        #     el_type="option",
        #     arr_name="selected",
        #     arr=selected,
        #     timeout=timeout,
        #     is_checked=True,
        # )

    def expect_choice_groups(
        self,
        # TODO-future; support patterns?
        choice_groups: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice groups of the input select to be an exact match.

        Parameters
        ----------
        choice_groups
            The expected choice groups of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """

        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(choice_groups) == 0:
            playwright_expect(self.loc_choice_groups).to_have_count(0, timeout=timeout)
            return

        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc_container,
            el_type="optgroup",
            arr_name="choice_groups",
            arr=choice_groups,
            timeout=timeout,
            key="label",
        )

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice labels of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected choice labels of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(value) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(value, timeout=timeout)

    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input selectize to allow multiple selections.

        Parameters
        ----------
        value
            Whether the input select allows multiple selections.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "multiple",
            value="" if value else None,
            timeout=timeout,
        )

    def expect_size(self, value: AttrValue, *, timeout: Timeout = None) -> None:
        """
        Expect the size attribute of the input select to have a specific value.

        Parameters
        ----------
        value
            The expected value of the `size` attribute.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        _expect_attribute_to_have_value(
            self.loc,
            "size",
            value=value,
            timeout=timeout,
        )


class InputSelectize(
    WidthContainerStyleM,
    UiWithLabel,
):
    """Controller for :func:`shiny.ui.input_selectize`."""

    def __init__(self, page: Page, id: str) -> None:
        super().__init__(page, id=id, loc=f"#{id} + .selectize-control")
        self._loc_dropdown = self.loc.locator("> .selectize-dropdown")
        self._loc_events = self.loc.locator("> .selectize-input")
        self._loc_selectize = self._loc_dropdown.locator(
            "> .selectize-dropdown-content"
        )
        self.loc = self.loc_container.locator(f"select#{id}")
        self.loc_choice_groups = self._loc_selectize.locator(
            "> .optgroup > .optgroup-header"
        )
        # Do not use `.option` class as we are not guaranteed to have it.
        # We are only guaranteed to have `data-value` attribute for each _option_
        self.loc_choices = self._loc_selectize.locator("[data-value]")
        self.loc_selected = self.loc_container.locator(f"select#{id} > option")

    def set(
        self,
        selected: str | list[str],
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Sets the selected option(s) of the input selectize.

        Selected items are altered as follows:
        1. Click on the selectize input to open the dropdown.
        2. Starting from the first selected item, each position in the currently selected list should match `selected`. If the item is not a match, remove it and try again.
        3. Add any remaining items in `selected` that are not currently selected by clicking on them in the dropdown.
        4. Press the `"Escape"` key to close the dropdown.

        Parameters
        ----------
        selected
            The [ordered] value(s) of the selected option(s).
        timeout
            The maximum time to wait for the selection to be set. Defaults to `None`.
        """

        def click_item(data_value: str, error_str: str) -> None:
            """
            Clicks the item in the dropdown by its `data-value` attribute.
            """
            if not isinstance(data_value, str):
                raise TypeError(error_str)

            # Wait for the item to exist
            playwright_expect(
                self._loc_selectize.locator(f"[data-value='{data_value}']")
            ).to_have_count(1, timeout=timeout)
            # Click the item
            self._loc_selectize.locator(f"[data-value='{data_value}']").click(
                timeout=timeout
            )

        # Make sure the selectize exists
        playwright_expect(self._loc_events).to_have_count(1, timeout=timeout)

        if self.loc.get_attribute("multiple") is None:
            # Single element selectize
            if isinstance(selected, list):
                if len(selected) != 1:
                    raise ValueError(
                        "Expected a `str` value (or a list of a single `str` value) when setting a single-select input."
                    )
                selected = selected[0]

            # Open the dropdown
            self._loc_events.click(timeout=timeout)

            try:
                # Click the item (which closes the dropdown)
                click_item(selected, "`selected=` value must be a `str`")
            finally:
                # Be sure to close the dropdown
                # (While this is not necessary on a sucessful `set()`, it is cleaner
                # than a catch all except)
                self._loc_events.press("Escape", timeout=timeout)

        else:
            # Multiple element selectize

            def delete_item(item_loc: Locator) -> None:
                """
                Deletes the item by clicking on it and pressing the Delete key.
                """

                item_loc.click()
                self.page.keyboard.press("Delete")

            if isinstance(selected, str):
                selected = [selected]
            if not isinstance(selected, list):
                raise TypeError(
                    "`selected=` must be a single `str` value or a list of `str` values when setting a multiple-select input"
                )

            # Open the dropdown
            self._loc_events.click()

            try:
                # Sift through the selected items
                # From left to right, we will remove ordered items that are not in the
                # ordered `selected`
                # If any selected items are not in the current selection, we will add
                # them at the end

                # All state transitions examples have an end goal of
                # A,B,C,D,E
                #
                # Items wrapped in `[]` are the item of interest at position `i`
                # Ex: `Z`,i=3 in A,B,C,[Z],E

                i = 0
                while i < self._loc_events.locator("> .item").count():
                    item_loc = self._loc_events.locator("> .item").nth(i)
                    item_data_value = item_loc.get_attribute("data-value")

                    # If the item has no data-value, remove it
                    # Transition: A,B,C,[?],D,E -> A,B,C,[D],E
                    if item_data_value is None:
                        delete_item(item_loc)
                        continue

                    # If there are more items than selected, remove the extras
                    # Transition: A,B,C,D,E,[Z] -> A,B,C,D,E,[]
                    if i >= len(selected):
                        delete_item(item_loc)
                        continue

                    selected_data_value = selected[i]

                    # If the item is not the next `selected` value, remove it
                    # Transition: A,B,[Z],C,D,E -> A,B,[C],D,E
                    if item_data_value != selected_data_value:
                        delete_item(item_loc)
                        continue

                    # The item is the next `selected` value
                    # Increment the index! (No need to remove it and add it back)
                    # A,B,[C],D,E -> A,B,C,[D],E
                    i += 1

                # Add the remaining items
                # A,B,[] -> A,B,C,D,E
                if i < len(selected):
                    for data_value in selected[i:]:
                        click_item(
                            data_value, f"`selected[{i}]=` value must be a `str`"
                        )

            finally:
                # Be sure to close the dropdown
                self._loc_events.press("Escape", timeout=timeout)
        return

    def expect_choices(
        self,
        choices: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the available options of the input selectize to be an exact match.

        Parameters
        ----------
        choices
            The expected choices of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, check for empty locator
        if len(choices) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return

        expect_locator_values_in_list(
            page=self.page,
            loc_container=self._loc_selectize,
            el_type=self.page.locator("[data-value]"),
            arr_name="choices",
            arr=choices,
            key="data-value",
            timeout=timeout,
        )

    def expect_selected(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the selected option(s) of the input select to be an exact match.

        Parameters
        ----------
        value
            The expected value(s) of the selected option(s).
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        # Playwright doesn't like lists of size 0
        if isinstance(value, list) and len(value) == 0:
            playwright_expect(self.loc_selected).to_have_count(0, timeout=timeout)
            return

        expect_locator_values_in_list(
            page=self.page,
            loc_container=self.loc,
            el_type=self.page.locator("> option"),
            arr_name="value",
            arr=value,
            key="value",
        )

    def _populate_dom(self, timeout: Timeout = None) -> None:
        """
        The click and Escape keypress is used to load the DOM elements
        """
        self._loc_events.click(timeout=timeout)
        _expect_style_to_have_value(
            self._loc_dropdown, "display", "block", timeout=timeout
        )
        self.page.locator("body").click(timeout=timeout)
        _expect_style_to_have_value(
            self._loc_dropdown, "display", "none", timeout=timeout
        )

    def expect_choice_groups(
        self,
        choice_groups: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice groups of the input select to be an exact match.

        Parameters
        ----------
        choice_groups
            The expected choice groups of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(choice_groups) == 0:
            playwright_expect(self.loc_choice_groups).to_have_count(0, timeout=timeout)
            return

        playwright_expect(self.loc_choice_groups).to_have_text(
            choice_groups, timeout=timeout
        )

    def expect_choice_labels(
        self,
        value: ListPatternOrStr,
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Expect the choice labels of the input selectize to be an exact match.

        Parameters
        ----------
        value
            The expected choice labels of the input select.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        self._populate_dom()
        # Playwright doesn't like lists of size 0. Instead, use `None`
        if len(value) == 0:
            playwright_expect(self.loc_choices).to_have_count(0, timeout=timeout)
            return
        playwright_expect(self.loc_choices).to_have_text(value, timeout=timeout)

    # multiple: bool = False,
    def expect_multiple(self, value: bool, *, timeout: Timeout = None) -> None:
        """
        Expect the input selectize to allow multiple selections.

        Parameters
        ----------
        value
            Whether the input select allows multiple selections.
        timeout
            The maximum time to wait for the expectation to be fulfilled. Defaults to `None`.
        """
        if value:
            _expect_attribute_to_have_value(
                self.loc, "multiple", "multiple", timeout=timeout
            )
        else:
            _expect_attribute_to_have_value(self.loc, "multiple", None, timeout=timeout)


class InputSlider(_InputSliderBase):
    """Controller for :func:`shiny.ui.input_slider`."""

    loc_irs_label: Locator
    """
    Playwright `Locator` of the input slider label.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSlider object.

        Parameters
        ----------
        page
            The Playwright Page object.
        id
            The id of the input element.
        """
        super().__init__(page, id=id)
        self.loc_irs_label = self.loc_irs.locator("> .irs > .irs-single")

    def expect_value(self, value: PatternOrStr, *, timeout: Timeout = None) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        playwright_expect(self.loc_irs_label).to_have_text(value, timeout=timeout)

    def set(
        self,
        value: str,
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
        """
        Set the value of the slider.

        Parameters
        ----------
        value
            The value to set the slider to.
        max_err_values
            The maximum number of error values to display if the value is not found. Defaults to 15.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        self._wait_for_container(timeout=timeout)

        handle = self.loc_irs.locator("> .irs-handle")
        self._set_helper(
            value=value,
            irs_label=self.loc_irs_label,
            handle=handle,
            max_err_values=max_err_values,
        )


class InputSliderRange(_InputSliderBase):
    """Controller for :func:`shiny.ui.input_slider` with a slider range."""

    loc_irs_label_from: Locator
    """
    Playwright `Locator` of the input slider label for the `from` handle.
    """
    loc_irs_label_to: Locator
    """
    Playwright `Locator` of the input slider label for the `to` handle.
    """

    def __init__(
        self,
        page: Page,
        id: str,
    ) -> None:
        """
        Initialize the InputSliderRange object.

        Parameters
        ----------
        page
            The Playwright Page object.
        id
            The id of the input element.
        """
        super().__init__(page, id=id)
        self.loc_irs_label_from = self.loc_irs.locator("> .irs > .irs-from")
        self.loc_irs_label_to = self.loc_irs.locator("> .irs > .irs-to")

    def expect_value(
        self,
        value: (
            typing.Tuple[PatternOrStr, PatternOrStr]
            | typing.Tuple[PatternOrStr, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, PatternOrStr]
        ),
        *,
        timeout: Timeout = None,
    ) -> None:
        """
        Asserts that the input element has the expected value.

        Parameters
        ----------
        value
            The expected value.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `value` tuple entries cannot be `MISSING_TYPE`")
        from_val = value[0]
        to_val = value[1]

        # TODO-future; Composable expectations
        if not_is_missing(from_val):
            playwright_expect(self.loc_irs_label_from).to_have_text(
                from_val, timeout=timeout
            )
        if not_is_missing(to_val):
            playwright_expect(self.loc_irs_label_to).to_have_text(
                to_val, timeout=timeout
            )

    def set(
        self,
        value: (
            typing.Tuple[str, str]
            | typing.Tuple[str, MISSING_TYPE]
            | typing.Tuple[MISSING_TYPE, str]
        ),
        *,
        max_err_values: int = 15,
        timeout: Timeout = None,
    ) -> None:
        """
        Set the value of the slider.

        Parameters
        ----------
        value
            The value to set the slider to.
        max_err_values
            The maximum number of error values to display if the value is not found. Defaults to 15.
        timeout
            The maximum time to wait for the value to appear. Defaults to `None`.
        """
        if all_missing(*value):
            raise ValueError("Both `value` tuple entries cannot be `MISSING_TYPE`")

        value_from = value[0]
        value_to = value[1]
        self.loc_container.wait_for(state="visible", timeout=timeout)
        self.loc_container.scroll_into_view_if_needed(timeout=timeout)
        handle_from = self.loc_irs.locator("> .irs-handle.from")
        handle_to = self.loc_irs.locator("> .irs-handle.to")

        def set_from() -> None:
            if not_is_missing(value_from):
                self._set_helper(
                    value=value_from,
                    irs_label=self.loc_irs_label_from,
                    handle=handle_from,
                    max_err_values=max_err_values,
                )

        def set_to() -> None:
            if not_is_missing(value_to):
                self._set_helper(
                    value=value_to,
                    irs_label=self.loc_irs_label_to,
                    handle=handle_to,
                    max_err_values=max_err_values,
                )

        # When moving both handles, order the moves so neither handle is clamped
        # by its sibling: moving `from` first is safe when it moves down or stays
        # put (`from_new <= from_old <= to_old`); otherwise the new range lies
        # entirely above the current `from` (`to_new >= from_new > from_old`), so
        # moving `to` first is safe.
        from_first = True
        if not_is_missing(value_from) and not_is_missing(value_to):
            state = self.loc.evaluate(self._SLIDER_STEP_STATE_JS, "from")
            labels = [str(label) for label in state["labels"]]
            # An unknown `from` value keeps the default order so that
            # `set_from()` raises the descriptive lookup error
            if value_from in labels:
                from_first = labels.index(value_from) <= int(state["cur"])

        if from_first:
            set_from()
            set_to()
        else:
            set_to()
            set_from()
