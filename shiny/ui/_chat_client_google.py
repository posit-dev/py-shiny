import sys
from typing import TYPE_CHECKING

from ._chat_client import LLMClient

if TYPE_CHECKING:
    if sys.version_info >= (3, 9):
        import google.generativeai.types as gtypes  # pyright: ignore[reportMissingTypeStubs]

        ContentDict = gtypes.ContentDict
    else:
        ContentDict = object


class GoogleClient(LLMClient["ContentDict"]):
    pass
