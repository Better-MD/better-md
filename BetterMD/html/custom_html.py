import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from ..elements.symbol import Symbol

T = t.TypeVar("T", default='Symbol')

class CustomHTML(t.Generic[T], ABC):
    @abstractmethod
    def to_html(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol') -> str: """
Generate an HTML representation of a symbol structure.

Subclasses must override this method to convert the provided symbol and its inner content into an
HTML string. The 'inner' list contains any child symbols, 'symbol' is the primary symbol to convert,
and 'parent' provides the context of the symbol's parent.
  
Returns:
    An HTML string representing the symbol structure.
"""
...

    def prepare(self, inner:'list[Symbol]', symbol:'T', parent:'Symbol'):"""
Prepares the components for HTML conversion.

This method serves as a hook for any preparatory processing on inner symbols,
the current symbol, and its parent before HTML rendering. Subclasses should
override this method to implement any domain-specific logic needed to adjust or
validate these elements prior to conversion.

Parameters:
    inner: List of symbols representing nested or inner elements.
    symbol: The symbol instance for the current element.
    parent: The parent symbol providing contextual hierarchy.
"""
...

    def verify(self, text) -> bool: ...