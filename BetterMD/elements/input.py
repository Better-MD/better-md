from .symbol import Symbol
from ..html import CustomHTML
from ..markdown import CustomMarkdown
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts an input symbol into its Markdown representation.
        
        If the symbol's "type" property is "checkbox", returns a Markdown formatted checkbox
        (with an "x" if checked or a space if unchecked) followed by the inner content's Markdown.
        Otherwise, returns the symbol's HTML representation.
        """
        if symbol.get_prop("type") == "checkbox":
            return f"- [{'x' if symbol.get_prop('checked', '') else ' '}] {inner.to_md()}"
        return symbol.to_html()

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Generate an RST formatted string for a checkbox input element.
        
        If the symbol's "type" property is "checkbox", returns a string displaying a checkbox
        indicator ("x" if the "checked" property is truthy, otherwise a blank space), optionally
        followed by the inner element’s RST representation. For other input types, returns an
        empty string.
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