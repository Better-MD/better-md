import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomHTML(t.Generic[T], ABC):
    @abstractmethod
    def to_html(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol') -> str: """
Generate an HTML string for a given symbol structure.

This abstract method must be implemented by subclasses to convert a symbol,
its inner content, and its parent context into an HTML representation.

Args:
    inner: A list of symbols representing the inner content.
    symbol: The symbol instance to be rendered.
    parent: The parent symbol providing contextual information.

Returns:
    The HTML string representation of the given symbol.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'):"""
Prepares symbols for HTML generation.

This method serves as a hook for pre-processing the provided symbol and its inner
content before HTML conversion. Subclasses can override this method to implement
custom preparatory behavior. By default, it performs no operations.

Args:
    inner: A list of Symbol objects representing nested elements.
    symbol: A symbol instance to be prepared for HTML processing.
    parent: The parent Symbol providing contextual reference.
"""
...

    def verify(self, text) -> bool: ...