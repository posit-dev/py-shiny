"""Facade classes for working with Shiny inputs/outputs in Playwright"""

from __future__ import annotations

import typing
from typing import Optional

OptionalStr = Optional[str]
OptionalInt = Optional[int]
OptionalFloat = Optional[float]
OptionalBool = Optional[bool]

PatternStr = typing.Pattern[str]
PatternOrStr = typing.Union[str, PatternStr]
ListPatternOrStr = typing.Union[
    typing.List[PatternOrStr], typing.List[str], typing.List[PatternStr]
]
AttrValue = typing.Union[PatternOrStr, None]
StyleValue = typing.Union[PatternOrStr, None]

Timeout = typing.Union[float, None]
