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
        raise ImportError(
            "Failed to download a default tokenizer. "
            "A tokenizer is required to impose `token_limits` on `chat.messages()`. "
            "To get a generic default tokenizer, install the `tokenizers` "
            "package (`pip install tokenizers`). "
        )
    except Exception as e:
        raise RuntimeError(
            "Failed to download a default tokenizer. "
            "A tokenizer is required to impose `token_limits` on `chat.messages()`. "
            "Try manually downloading a tokenizer using "
            "`tokenizers.Tokenizer.from_pretrained()` and passing it to `ui.Chat()`."
            f"Error: {e}"
        ) from e
