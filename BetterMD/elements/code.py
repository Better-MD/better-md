from .symbol import Symbol
from .text import Text
from ..markdown import CustomMarkdown
from ..html import CustomHTML
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Convert content to Markdown code.
        
        Transforms the provided content into its Markdown representation. If a language is specified
        via the symbol or the content contains newline characters, the content is wrapped in a fenced
        code block with the optional language identifier; otherwise, it is formatted as inline code.
        If the input is a Text instance, it is first converted to Markdown.
            
        Returns:
            str: The Markdown-formatted code.
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
        Converts inner elements to an HTML code element with optional syntax highlighting.
        
        Joins the HTML representations of each inner element with newline characters and
        wraps the result in a <code> tag. If a programming language is specified in the symbol's
        properties, the code element is assigned a language-specific class.
        """
        language = symbol.get_prop("language", "")
        inner = "\n".join([i.to_html() for i in inner])
        
        if language:
            return f'<code class="language-{language}">{inner}</code>'
        
        return f"<code>{inner}</code>"
    
    def verify(self, text: str) -> bool:
        """
        Verifies that the input text equals "code" in a case-insensitive manner.
        
        Args:
            text: The string to validate against the keyword "code".
        
        Returns:
            True if the lowercase version of text is "code", otherwise False.
        """
        return text.lower() == "code"

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Convert content to a reStructuredText format.
        
        This method transforms the provided content into reStructuredText syntax suited for code
        representation. It extracts an optional programming language from the symbol and processes the
        inner content accordingly. When a language is specified or the content spans multiple lines, it
        formats the content as an indented code block—using a language-specific code-block directive if
        available or a literal block if not. Otherwise, the content is formatted as inline code with backticks
        properly escaped if necessary.
        
        Parameters:
            inner: The content to convert, which may be a list of elements or a single element. Each item is
                   either an object with its own RST conversion method or is convertible to a string.
            symbol: An object that provides properties (including a "language" attribute) for determining
                    code block formatting.
            parent: A contextual parameter that is part of the interface but is not used in this conversion.
        
        Returns:
            A string containing the content formatted in reStructuredText.
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