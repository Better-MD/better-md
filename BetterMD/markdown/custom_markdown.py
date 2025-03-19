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
Convert a symbol structure to its markdown representation.

Subclasses must implement this method to produce a markdown formatted string using the
provided inner symbols, target symbol, and contextual parent symbol.

Args:
    inner: A list of Symbol instances representing nested content.
    symbol: The symbol to be converted.
    parent: The parent Symbol providing contextual hierarchy.

Returns:
    A markdown string corresponding to the symbol conversion.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'): """
Performs preparation before markdown conversion.

This placeholder method can be overridden to preprocess or modify the provided
symbol data and context before the actual markdown generation. By default, it
performs no action.

Args:
    inner (list[Symbol]): List of symbol objects representing nested content.
    symbol (T): The target symbol for markdown conversion.
    parent (Symbol): The parent symbol providing contextual information.
"""
...

    def verify(self, text) -> bool: """
Verify the provided markdown text.

Args:
    text: The markdown text to validate.

Returns:
    bool: True if the text conforms to the expected markdown format, otherwise False.
"""
...
