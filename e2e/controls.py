"""Facade classes for working with Shiny inputs/outputs in Playwright"""

# pyright: reportUnknownMemberType=false

from typing import List
from playwright.sync_api import Locator, Page, expect


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

    def get_slider_value(self) -> str:
        return self.loc.locator(".irs-single").inner_text()

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

    # TODO
    # def get_options(self):

    def get_selected(self):
        return self.loc.locator("option[selected]").inner_text()

    def select_option(self, value: str):
        self.loc.select_option(value)

class SelectizeInput():
    def __init__(self, page: Page, inputId: str):
        self.page = page
        self.loc = page.locator(f"//*[@id='{inputId}']//ancestor::div[contains(@class, 'shiny-input-container')]")

    def get_selected_items(self) -> List:
        selected_items = self.loc.locator(".selectize-input .item")
        mylist = []
        for i in range(selected_items.count()):
            mylist.append(selected_items.nth(i).inner_text())

        return mylist

    def select_option(self, value: str):
        self.loc.locator(".selectize-input").click()

        dropdown = self.loc.locator(".selectize-dropdown")
        expect(dropdown).to_be_visible()

        self.loc.locator(f".selectize-dropdown-content .option[data-value='{value}']").click()

        self.loc.locator(f".selectize-input .item[data-value='{value}']")

        # click outside the dropdown box to close the dropdown menu
        self.page.keyboard.press("Escape")

    #TODO
    #def remove_option(self):


class FileInput():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"//*[@id='{inputId}']//parent::div[contains(@class, 'shiny-input-container')]")

    def upload_file(self, fileName: str) -> None:
        browse = self.loc.locator("//span[contains(@class, 'btn-file')]")
        #TODO: Enhancement: Check PurePath option to upload files
        browse.set_input_files(files=[f"e2e/data-files/{fileName}"])

# Shiny Outputs
class TextOutput():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.shiny-text-output.shiny-bound-output")

    def get_text(self) -> str:
        return self.loc.inner_text()

    def contains_digit(self, text: str) -> bool:
        for character in text:
            if character.isdigit():
                return True
        return False





# Other
class ActionButton():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.action-button.shiny-bound-input")

class DownloadButton():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId}.shiny-download-link.shiny-bound-output")

class NavControls():
    '''navControlType represents the type of navigation options available
    for example: navset_tab, navset_pill, navset_tab_card, navset_pill_card, navset_pill_list'''

    def __init__(self, page: Page, navControlType: str, navItem: str):
        self.loc = page.locator(f".nav.{navControlType} .nav-item a[data-value={navItem}]")

class LeafletContainer():
    def __init__(self, page: Page, inputId: str):
        self.loc = page.locator(f"#{inputId} .leaflet-container")

    @property
    def expect(self):
        return expect(self.loc)

    def locate_map_output(self) -> Locator:
        return self.loc.locator("xpath=..").locator("xpath=..").locator("shiny-ipywidget-output shiny-bound-output")

    def map_zoom_in(self):
        return self.loc.locator(".leaflet-control-zoom-in")

    def map_zoom_out(self):
        return self.loc.locator(".leaflet-control-zoom-out")




