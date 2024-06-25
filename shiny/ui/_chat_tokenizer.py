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
            "shiny's `Chat` is unable to impose"
            "Unable to obtain a default tokenizer without the `tokenizers` package. "
            "Please install it.",
            stacklevel=2,
        )
        return None
    except Exception:
        warnings.warn(
            "Unable to obtain a default tokenizer. "
            "Consider setting the tokenizer manually via `Chat()`'s `tokenizer` parameter.",
            stacklevel=2,
        )
        return None
