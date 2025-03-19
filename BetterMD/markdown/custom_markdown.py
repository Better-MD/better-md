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
Converts the provided symbols to a markdown string.

Subclasses must implement this method to generate a markdown representation based on a list of inner symbols, a specific symbol, and its parent symbol.

Args:
    inner: A list of symbols to be included in the markdown content.
    symbol: The symbol to be processed.
    parent: The parent symbol providing contextual hierarchy.

Returns:
    A markdown-formatted string.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """Prepare markdown content from symbols.

Hook method for subclasses to perform any required pre-processing before generating the
final markdown output. It receives a list of inner symbols, the current symbol being processed,
and its parent symbol to allow contextual adjustments. By default, this method does nothing.
"""
...

    def verify(self, text) -> bool: """Verify that the provided text meets the expected criteria.

Assesses whether the specified text conforms to custom markdown validation rules.
Returns True if the text is valid according to these rules, otherwise False.

Args:
    text: The text to verify.
"""
...
