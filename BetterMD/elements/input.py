from .symbol import Symbol
from ..html import CustomHTML
from ..markdown import CustomMarkdown
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Convert an input element to its Markdown representation.
        
        If the symbol represents a checkbox, returns a Markdown-formatted checklist item
        with an 'x' when checked (or a space when unchecked) followed by the rendered inner content.
        For other input types, the element’s HTML representation is returned.
        
        Parameters:
            inner: An object with a to_md() method that renders inner content.
            symbol: An element descriptor whose 'type' property determines rendering; if its 'type'
                    is "checkbox", the 'checked' property is used to indicate its state.
            parent: The parent element context (unused in this conversion).
        
        Returns:
            A string containing either the Markdown or HTML representation of the input element.
        """
        if symbol.get_prop("type") == "checkbox":
            return f"- [{'x' if symbol.get_prop('checked', '') else ' '}] {inner.to_md()}"
        return symbol.to_html()

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Return a reStructuredText representation of a checkbox input element.
        
        If the symbol's "type" property is "checkbox", formats a checkbox with an "x"
        if checked (or a space if not) and appends any nested content rendered via its
        to_rst method. For input types other than checkbox, returns an empty string.
        
        Args:
            inner: An optional element to be rendered in RST, if provided.
            symbol: The input element symbol whose properties determine formatting.
            parent: The parent element; not used in this conversion.
        
        Returns:
            A string with the RST representation of the checkbox input, or an empty
            string.
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