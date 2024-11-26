from __future__ import annotations

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


def get_default_tokenizer() -> TokenizersTokenizer:
    try:
        from tokenizers import Tokenizer

        return Tokenizer.from_pretrained("bert-base-cased")  # type: ignore
    except ImportError:
        raise ValueError(
            "A tokenizer is required to impose `token_limits` on messages. "
            "To get a generic default tokenizer, install the `tokenizers` "
            "package (`pip install tokenizers`). "
            "To get a more precise token count, provide a specific tokenizer "
            "to the `Chat` constructor."
        )
    except Exception as e:
        raise ValueError(
            "Failed to load the default tokenizer. "
            "Ensure that the `tokenizers` package is installed and "
            "that the `bert-base-cased` model is available. "
            f"Error: {e}"
        ) from e
