from typing import Text
from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .text import Text

class MD(CustomMarkdown):
    def to_md(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Converts a title element into its Markdown representation.
        
        Expects the content list to contain exactly one Text element; otherwise,
        raises a ValueError. The resulting string is formatted as: title: "<text>".
         
        Args:
            inner: A list of Symbol objects representing the title content. Must contain
                   exactly one Text element.
            symbol: The Symbol instance corresponding to the title element.
            parent: The parent Symbol of the title element.
            **kwargs: Additional keyword arguments (unused).
            
        Returns:
            A Markdown-formatted title string.
            
        Raises:
            ValueError: If the inner list does not contain exactly one Text element.
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f'title: "{inner[0].to_md()}"'

class RST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Converts a title element to reStructuredText format.
        
        This method expects the 'inner' list to contain exactly one Text element representing the title.
        It returns the title as a reStructuredText string prefixed with ":title: ".
        Raises:
            ValueError: If 'inner' does not contain exactly one Text element.
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f":title: {inner[0].to_rst()}"


class Title(Symbol):
    html = "title"
    md = MD()
    rst = RST()


