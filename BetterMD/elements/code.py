from .symbol import Symbol
from .text import Text
from ..markdown import CustomMarkdown
from ..html import CustomHTML
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Convert the given content into Markdown code formatting.
        
        This method transforms the provided content based on the symbol's properties. If the symbol specifies a programming language or the content contains newlines, the content is formatted as a fenced code block using triple backticks. Otherwise, the content is enclosed in single backticks as inline code. If the content is a Text instance, it is first converted to Markdown.
        
        Args:
            inner: The content to format as Markdown, which may be a string or a Text instance.
            symbol: An object containing properties (e.g., language) that influence the formatting.
            parent: The parent context element (unused) for interface consistency.
        
        Returns:
            A Markdown-formatted string representing the content as a code block or inline code.
        """
        language = symbol.get_prop("language", "")
        if isinstance(inner, Text):
            inner = inner.to_md()
        
        # If it's a code block (has language or multiline)
        if language or "\n" in inner:
            return f"```{language}\n{inner}\n```\n"
        
        # Inline code
        return f"`{inner}`"

class HTML(CustomHTML):
    def to_html(self, inner, symbol, parent):
        """
        Converts a collection of content elements into an HTML code block.
        
        Joins the HTML representation of each item and wraps the result in a <code> element.
        If the symbol specifies a programming language, the <code> tag includes a
        language-specific CSS class for syntax highlighting.
        """
        language = symbol.get_prop("language", "")
        inner = "\n".join([i.to_html() for i in inner])
        
        if language:
            return f'<code class="language-{language}">{inner}</code>'
        
        return f"<code>{inner}</code>"
    
    def verify(self, text: str) -> bool:
        """
        Determine if the provided text equals "code", case-insensitively.
        
        Args:
            text: The text to check.
        
        Returns:
            bool: True if the text matches "code" irrespective of case, otherwise False.
        """
        return text.lower() == "code"

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Converts content to reStructuredText formatted code.
        
        This method processes the given content—either a single element or a list—and converts it into a
        reStructuredText representation. It extracts a language property from the provided symbol to determine
        if the output should be formatted as a code block. When a language is specified or the content spans
        multiple lines, the content is indented and returned as a code block (using the ".. code-block::"
        directive if a language is provided, or a literal block otherwise). Inline code is wrapped in backticks,
        with special handling if backticks already exist in the content.
        
        Args:
            inner: The content to convert, which may be a single element or a list of elements.
            symbol: An object that supplies properties (such as the programming language) affecting formatting.
            parent: Unused parameter reserved for interface compatibility.
        
        Returns:
            A string containing the reStructuredText formatted code, either as a code block or inline code.
        """
        language = symbol.get_prop("language", "")
        
        # Handle inner content
        if isinstance(inner, list):
            content = "".join([
                i.to_rst() if isinstance(i, Symbol) else str(i)
                for i in inner
            ])
        else:
            content = inner.to_rst() if isinstance(inner, Symbol) else str(inner)
        
        # If it's a code block (has language or multiline)
        if language or "\n" in content:
            # Use code-block directive for language-specific blocks
            if language:
                # Indent the content by 3 spaces (RST requirement)
                indented_content = "\n".join(f"   {line}" for line in content.strip().split("\n"))
                return f".. code-block:: {language}\n\n{indented_content}\n\n"
            
            # Use simple literal block for language-less blocks
            # Indent the content by 3 spaces (RST requirement)
            indented_content = "\n".join(f"   {line}" for line in content.strip().split("\n"))
            return f"::\n\n{indented_content}\n\n"
        
        # Inline code
        # Escape backticks if they exist in content
        if "`" in content:
            return f"``{content}``"
        return f"`{content}`"

class Code(Symbol):
    html = HTML()
    md = MD()
    rst = RST()
    nl = True 