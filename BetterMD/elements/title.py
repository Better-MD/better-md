from typing import Text
from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .text import Text

class MD(CustomMarkdown):
    def to_md(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Converts a title element to its Markdown representation.
        
        This method expects the 'inner' parameter to be a list containing exactly one
        Text element. The title text is converted using its to_md() method and formatted
        into a Markdown title declaration. A ValueError is raised if 'inner' does not meet
        the expected criteria.
        
        Args:
            inner: A list of Symbol objects that must contain a single Text instance.
        
        Returns:
            A string representing the title in Markdown format.
        
        Raises:
            ValueError: If 'inner' does not contain exactly one Text element.
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f'title: "{inner[0].to_md()}"'

class RST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Convert a title element to reStructuredText format.
        
        Validates that the provided list contains exactly one Text element, raising a
        ValueError if this condition is not met.
        
        Args:
            inner: A list of Symbol objects representing the title content, which must
                   consist of a single Text element.
        
        Returns:
            A reStructuredText formatted title string prefixed with ":title: ".
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f":title: {inner[0].to_rst()}"


class Title(Symbol):
    html = "title"
    md = MD()
    rst = RST()


