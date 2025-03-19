from typing import Text
from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .text import Text

class MD(CustomMarkdown):
    def to_md(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Converts a single Text element to a Markdown title.
        
        This method verifies that the provided list contains exactly one element and that
        this element is a Text instance. If the check passes, it returns a Markdown-formatted
        title using the element's own conversion method; otherwise, a ValueError is raised.
        
        Args:
            inner: A list of Symbol objects that must contain exactly one Text instance.
        
        Raises:
            ValueError: If the inner list does not contain exactly one Text element.
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f'title: "{inner[0].to_md()}"'

class RST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol, **kwargs) -> str:
        """
        Generates a reStructuredText title string from a single Text element.
        
        Validates that the inner list contains exactly one Text instance and returns a formatted
        string prefixed with ":title:" followed by the element’s RST representation. Raises a
        ValueError if the validation fails.
        """
        if not isinstance(inner[0], Text) or len(inner) != 1:
            raise ValueError("Title element must contain a single Text element")
        
        return f":title: {inner[0].to_rst()}"


class Title(Symbol):
    html = "title"
    md = MD()
    rst = RST()


