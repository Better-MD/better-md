import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomMarkdown(t.Generic[T], ABC):
    prop = ""
    md: 'dict[str, str]' = {}

    @abstractmethod
    def to_md(self, inner: 'list[Symbol]', symbol:'T', parent:'Symbol') -> str: """
Converts a symbol along with its inner elements to a Markdown string.

Subclasses must implement this method to generate a Markdown
representation based on the provided current symbol, its nested child
symbols, and its parent context.

Args:
    inner: A list of child symbols to be processed.
    symbol: The symbol to convert.
    parent: The contextual parent symbol of the given symbol.

Returns:
    The resulting Markdown string.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """
Performs any necessary preparation prior to markdown conversion.

This hook allows subclasses to preprocess symbols before generating
their markdown representation.

Args:
    inner: A list of symbols representing nested elements.
    symbol: The current symbol to be prepared.
    parent: The parent symbol related to the current symbol.
"""
...

    def verify(self, text) -> bool: """
Verifies whether the provided text meets the expected criteria.

This method should determine if the given text is valid according to the custom rules
defined in a subclass. It returns True if the text passes validation, otherwise False.

Args:
    text: The text content to verify.
"""
...
