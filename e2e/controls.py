"""Facade classes for working with Shiny inputs/outputs in Playwright"""

# pyright: reportUnknownMemberType=false

from playwright.sync_api import Locator, Page, expect
from pathlib import PurePath


class SimpleInput:
    def __init__(self, page: Page, selector: str):
        self.loc = page.locator(selector)

    @property
    def expect(self):
        return expect(self.loc)


class TextInput(SimpleInput):
    def __init__(self, page: Page, inputId: str):
        super().__init__(page, f"input#{inputId}[type=text].shiny-bound-input")


class TextAreaInput(SimpleInput):
    def __init__(self, page: Page, inputId: str):
        super().__init__(page, f"textarea#{inputId}.shiny-bound-input")


class NumericInput(SimpleInput):
    def __init__(self, page: Page, inputId: str):
        super().__init__(page, f"input#{inputId}[type=number].shiny-bound-input")


class CheckboxInput(SimpleInput):
    def __init__(self, page: Page, inputId: str):
        super().__init__(page, f"input#{inputId}[type=checkbox].shiny-bound-input")

class DateInput:
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}")

    @property
    def expect(self):
        return expect(self.loc.locator("input"))


class DateRangeInput:
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}")

    @property
    def expect_start(self):
        return expect(self.loc.locator("input:first-of-type"))

    @property
    def expect_end(self):
        return expect(self.loc.locator("input:last-of-type"))


class SliderInput:
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.js-range-slider").locator("xpath=..")

    def map_slider(self, page: Page, inputId: str):
        return page.locator(f"#{inputId}").locator("xpath=../span")

    def move_slider(self, fraction: float) -> None:
        self.loc.wait_for(state="visible")
        self.loc.scroll_into_view_if_needed()

        handle = self.loc.locator(".irs-handle")
        handle_bb = handle.bounding_box()
        if handle_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-handle")

        handle_center = (
            handle_bb.get("x") + (handle_bb.get("width") / 2),
            handle_bb.get("y") + (handle_bb.get("height") / 2),
        )

        grid = self.loc.locator(".irs-grid")
        grid_bb = grid.bounding_box()
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-grid")

        mouse = self.loc.page.mouse
        mouse.move(handle_center[0], handle_center[1])
        mouse.down()
        mouse.move(
            grid_bb.get("x") + (fraction * grid_bb.get("width")), handle_center[1]
        )
        mouse.up()

    def move_slider_range(self, fractionFrom: float, fractionTo: float) -> None:
        self.loc.wait_for(state="visible")
        self.loc.scroll_into_view_if_needed()

        # First Handle
        handle_first = self.loc.locator(".irs-handle.from")
        handle_bb_first = handle_first.bounding_box()
        if handle_bb_first is None:
            raise RuntimeError("Couldn't find bounding box for .irs-handle")

        handle_center_first = (
            handle_bb_first.get("x") + (handle_bb_first.get("width") / 2),
            handle_bb_first.get("y") + (handle_bb_first.get("height") / 2),
        )

        grid = self.loc.locator(".irs-grid")
        grid_bb = grid.bounding_box()
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-grid")

        mouse = self.loc.page.mouse
        mouse.move(handle_center_first[0], handle_center_first[1])
        mouse.down()
        mouse.move(
            grid_bb.get("x") + (fractionFrom * grid_bb.get("width")), handle_center_first[1]
        )

        # Second Handle
        handle_second = self.loc.locator(".irs-handle.to")
        handle_bb_second = handle_second.bounding_box()
        if handle_bb_second is None:
            raise RuntimeError("Couldn't find bounding box for .irs-handle")

        handle_center_second = (
            handle_bb_second.get("x") + (handle_bb_first.get("width") / 2),
            handle_bb_second.get("y") + (handle_bb_first.get("height") / 2),
        )

        grid = self.loc.locator(".irs-grid")
        grid_bb = grid.bounding_box()
        if grid_bb is None:
            raise RuntimeError("Couldn't find bounding box for .irs-grid")

        mouse = self.loc.page.mouse
        mouse.move(handle_center_second[0], handle_center_second[1])
        mouse.down()
        mouse.move(
            grid_bb.get("x") + (fractionTo * grid_bb.get("width")), handle_center_second[1]
        )




class CheckboxGroupInput:
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.shiny-input-checkboxgroup")

    def locate_by_label(self, label: str) -> Locator:
        return self.loc.locator(
            ".shiny-options-group .checkbox",
            has=self.loc.page.locator("span", has_text=label),
        ).locator("input[type=checkbox]")

    def locate_by_value(self, value: str) -> Locator:
        return self.loc.locator("input[type=checkbox][value={value}]")


class RadioButtonsInput:
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.shiny-input-radiogroup")

    def locate_by_label(self, label: str) -> Locator:
        return self.loc.locator(
            ".shiny-options-group .radio",
            has=self.loc.page.locator("span", has_text=label),
        ).locator("input[type=radio]")

    def locate_by_value(self, value: str) -> Locator:
        return self.loc.locator("input[type=radio][value={value}]")

class SelectInput(SimpleInput):
    def __init__(self, page: Page, inputId: str):
        super().__init__(page, f"select#{inputId}.shiny-bound-input")

    def get_selected(self):
        return self.loc.locator("option[selected]").inner_text()

    def select_option(self, value: str):
        self.loc.select_option(value)

class FileInput():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}[type=file].shiny-bound-input")

    #TODO
    # def upload_file(self, file) -> None:
    #     browse = self.loc.locator("xpath=..")
    #     browse.set_input_files(here / "../examples" / example_name / "app.py", scope)

class ActionButton():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.action-button.shiny-bound-input")

