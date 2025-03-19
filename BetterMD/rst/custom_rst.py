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
Convert a symbol and its children into reStructuredText format.

This abstract method converts the provided symbol into its corresponding reStructuredText
representation. The conversion may incorporate nested symbols from the inner list to form a
complete and structured output.

Args:
    inner: A list of child symbols to include in the conversion.
    symbol: The symbol to be converted.
    parent: The parent symbol providing contextual information.

Returns:
    A string representing the reStructuredText formatted output.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """
Prepares contextual data for reStructuredText conversion.

This method provides a hook for performing any necessary preparatory tasks prior to
conversion. Subclasses may override this method to initialize internal state or
modify the provided symbols based on their context.

Parameters:
    inner: A list of symbols representing inner content.
    symbol: The symbol to be prepared.
    parent: The parent symbol associated with the current symbol.
"""
...

    def verify(self, text) -> 'bool': """
Verifies if the given text meets the required validation criteria.

This method checks whether the provided text conforms to the expected rules or format.
It returns True when the text is valid, and False otherwise.

Args:
    text: The text string to validate.

Returns:
    bool: True if the text passes validation, False otherwise.
"""
...