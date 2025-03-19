import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomRst(t.Generic[T], ABC):
    prop = ""
    rst: 'dict[str, str]' = {}

    @abstractmethod
    def to_rst(self, inner: 'list[Symbol]', symbol:'T', parent:'Symbol') -> 'str': """
Converts provided symbols into a reStructuredText formatted string.

Subclasses must override this method to implement conversion logic that transforms the
current symbol, its nested inner symbols, and the contextual parent symbol into a
reStructuredText representation.

Args:
    inner: A list of symbols representing nested content.
    symbol: The symbol instance to be converted.
    parent: The parent symbol providing contextual information.

Returns:
    A string containing the reStructuredText representation.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """
Prepare context for reStructuredText conversion.

Subclasses may override this method to perform any preparatory actions before
rendering a symbol into reStructuredText format. The provided parameters supply
context for the conversion process.

Args:
    inner: A list of symbols representing nested or inner elements.
    symbol: The symbol to be processed.
    parent: The parent symbol of the current symbol.
"""
...

    def verify(self, text) -> 'bool': """
Verify the validity of the provided text.

This method should assess whether the given text meets the required criteria.
Subclasses must override this method to implement the specific verification logic.

Args:
    text: The text to be validated.

Returns:
    bool: True if the text is valid, False otherwise.
"""
...