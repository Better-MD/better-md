from .symbol import Symbol
from ..html import CustomHTML
from ..markdown import CustomMarkdown
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts an input symbol to its Markdown representation.
        
        If the symbol is of type "checkbox", returns a Markdown list item that displays the 
        checkbox's status ("x" if checked, a space if not) followed by the inner content’s Markdown.
        For other types, returns the symbol’s HTML representation.
        """
        if symbol.get_prop("type") == "checkbox":
            return f"- [{'x' if symbol.get_prop('checked', '') else ' '}] {inner.to_md()}"
        return symbol.to_html()

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Generate a reStructuredText representation of an input symbol.
        
        If the symbol's type is "checkbox", returns a formatted checkbox with an "x" when checked or a space when not, optionally followed by inner content rendered in RST. For other input types, returns an empty string.
        """
        if symbol.get_prop("type") == "checkbox":
            return f"[{'x' if symbol.get_prop('checked', '') else ' '}] {inner.to_rst() if inner else ''}"
        return ""  # Most input types don't have RST equivalents

class Input(Symbol):
    # Common input attributes
    prop_list = [
        "type",
        "name",
        "value",
        "placeholder",
        "required",
        "disabled",
        "readonly",
        "min",
        "max",
        "pattern",
        "autocomplete",
        "autofocus",
        "checked",
        "multiple",
        "step"
    ]
    html = "input"
    md = MD()
    rst = RST()