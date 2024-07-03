from __future__ import annotations

import warnings
from typing import (
    AbstractSet,
    Any,
    Collection,
    Literal,
    Protocol,
    Union,
    runtime_checkable,
)


# A duck type for tiktoken.Encoding
class TiktokenEncoding(Protocol):
    name: str

    def encode(
        self,
        text: str,
        *,
        allowed_special: Union[Literal["all"], AbstractSet[str]] = set(),  # noqa: B006
        disallowed_special: Union[Literal["all"], Collection[str]] = "all",
    ) -> list[int]: ...


# A duck type for tokenizers.Encoding
@runtime_checkable
class TokenizersEncoding(Protocol):
    @property
    def ids(self) -> list[int]: ...


# A duck type for tokenizers.Tokenizer
class TokenizersTokenizer(Protocol):
    def encode(
        self,
        sequence: Any,
        pair: Any = None,
        is_pretokenized: bool = False,
        add_special_tokens: bool = True,
    ) -> TokenizersEncoding: ...


TokenEncoding = Union[TiktokenEncoding, TokenizersTokenizer]


def get_default_tokenizer() -> TokenizersTokenizer | None:
    try:
        from tokenizers import Tokenizer

        return Tokenizer.from_pretrained("bert-base-cased")  # type: ignore
    except ImportError:
        warnings.warn(
            "`Chat` is unable obtain a default tokenizer without the `tokenizers` "
            "package installed. Please `pip install tokenizers` or set "
            "`Chat(tokenizer=None)` to disable tokenization.",
            stacklevel=2,
        )
        return None
    except Exception:
        warnings.warn(
            "Unable to obtain a default tokenizer. "
            "Consider providing one to `Chat()`'s `tokenizer` parameter "
            "(or set it to `None` to disable tokenization).",
            stacklevel=2,
        )
        return None
