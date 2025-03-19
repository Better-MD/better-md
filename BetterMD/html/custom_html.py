import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomHTML(t.Generic[T], ABC):
    @abstractmethod
    def to_html(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol') -> str: """
Converts a symbol and its context into an HTML string.

This abstract method should be implemented by subclasses to generate an HTML
representation from the provided symbol, its inner content, and its parent.

Args:
    inner: A list of inner symbols to be included in the HTML.
    symbol: The symbol to be rendered as HTML.
    parent: The parent symbol providing contextual information.

Returns:
    A string containing the HTML representation.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'):"""
Prepare the HTML element for conversion.

This method serves as a hook for performing any preparatory operations on the
element's content prior to HTML conversion. Subclasses can override this method
to implement custom preprocessing logic using the provided inner elements,
the current symbol, and its parent symbol.

Args:
    inner: A list of Symbol instances representing the inner content.
    symbol: The symbol representing the current element.
    parent: The symbol representing the parent element.
"""
...

    def verify(self, text) -> bool: ...