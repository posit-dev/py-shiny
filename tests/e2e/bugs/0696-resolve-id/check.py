from __future__ import annotations

# Make check to determine if all of shiny.ui is accounted for. Prevent new UI methods from being added without making sure they have module support or could be black listed from the check
# this is a proof of concept of how it can be done.. if the number of items not listed anywhere is > 0 then we fail the test
import datetime
from typing import NamedTuple

from app import input_keys, x_input_keys

# TODO-karan: Verify inputs work within modules
# From https://github.com/posit-dev/py-shiny/pull/731#discussion_r1336102593:
# I like this idea and where it's going...
#
# - [ ] Move `test_0696_resolve_id.py`'s custom expectation method into a new file (`mod_state.py`?) that can be imported into here and the original file.
# - [x] Change class name to `ModState`
# - [ ] Have expectation methods receive a `ModState` object.
# - [ ] Double check if a value is missing when creating a NamedTuple, an error is thrown.
# - [ ] Have a `default_mod_state` object (which currently equals `component` above).
# - [ ] Is it possible to import `mod_state` into the app to retrieve the `input_keys` and `x_input_keys`?


class ModState(NamedTuple):
    sidebar: bool
    accordion: tuple[str, ...]
    popover: bool
    tooltip: bool
    input_action_button: int
    input_action_link: int
    input_file: str | None
    input_checkbox: bool
    input_checkbox_group: tuple[str, ...]
    input_date: datetime.date | str
    input_date_range: tuple[datetime.date, datetime.date]
    input_numeric: int
    input_password: str
    input_radio_buttons: str
    input_select: str
    input_selectize: str
    input_slider: int
    input_switch: bool
    input_text: str
    input_text_area: str
    navset_bar: str
    navset_card_pill: str
    navset_card_tab: str
    navset_hidden: str
    navset_pill: str
    navset_tab: str


blacklist = set(["awesome_component"])

x_input_keys = ("x_" + key for key in x_input_keys)

component = ModState(
    sidebar=True,
    accordion=("a",),
    popover=False,
    tooltip=False,
    input_action_button=0,
    input_action_link=0,
    input_file=None,
    input_checkbox=False,
    input_checkbox_group=("b", "c", "d"),
    input_date=datetime.date(2023, 8, 24),
    input_date_range=(datetime.date(2023, 8, 25), datetime.date(2023, 8, 27)),
    input_numeric=0,
    input_password="password0",
    input_radio_buttons="a",
    input_select="a",
    input_selectize="a",
    input_slider=0,
    input_switch=False,
    input_text="text0",
    input_text_area="text_area0",
    navset_bar="a",
    navset_card_pill="a",
    navset_card_tab="a",
    navset_hidden="a",
    navset_pill="a",
    navset_tab="a",
)

not_in_production = set(component._fields) - set(input_keys)
not_in_experimental = not_in_production - set(x_input_keys)
not_listed = not_in_experimental - blacklist
# TODO-karan: Turn into assertions
print(f" Items not in production are {not_in_production}")
print(f" Items not in experimental are {not_in_experimental}")
print(f"Number of items not listed anywhere are {len(not_listed)}")
