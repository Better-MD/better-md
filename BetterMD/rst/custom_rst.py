import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomRst(t.Generic[T], ABC):
    prop = ""
    rst: 'dict[str, str]' = {}

    @abstractmethod
    def to_rst(self, inner: 'list[Symbol]', symbol:'T', parent:'Symbol') -> 'str': """Generate a reStructuredText representation for a symbol.

Subclasses must implement this method to convert the current symbol into an RST
formatted string by utilizing its nested inner symbols and the context provided by
the parent symbol.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """
Prepares the symbols for reStructuredText conversion.

This method processes a list of symbols along with a primary symbol and its parent
to perform any necessary preparation before generating reStructuredText output.
Subclasses may override this method to implement custom pre-processing logic.

Args:
    inner: A list of symbols representing inner content.
    symbol: The primary symbol to be processed.
    parent: The parent symbol associated with the primary symbol.
"""
...

    def verify(self, text) -> 'bool': """
Verifies whether the provided text meets the expected criteria.

This method checks if the given text adheres to the required rules for custom
reStructuredText processing. Subclasses should override this method to implement
specific validation logic.

Args:
    text: The text content to validate.

Returns:
    True if the text passes verification; otherwise, False.
"""
...