from .symbol import Symbol
from .text import Text
from ..markdown import CustomMarkdown
from ..html import CustomHTML
from ..rst import CustomRst

class MD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts content into Markdown code formatting.
        
        If the input is a Text instance, it is first converted using its own Markdown method. When a language is specified in the symbol or the content is multiline, the method formats the content as a code block with triple backticks and a language identifier. Otherwise, it returns the content wrapped in single backticks for inline code.
        
        Parameters:
            inner: The content to convert, which may be a raw string or a Text object.
            symbol: An object from which the programming language is retrieved.
            parent: A placeholder parameter for the parent element (currently unused).
        
        Returns:
            A string containing the Markdown formatted code.
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
        Generate HTML markup for a code block.
        
        Converts a list of elements to their HTML representations by joining the results
        of each item’s `to_html()` method with newline characters, and wraps the result in an
        HTML <code> tag. If the symbol specifies a programming language via its 'language'
        property, a corresponding language-specific class is added to the tag.
        
        Parameters:
            inner: A list of objects with a `to_html()` method.
            symbol: An object with properties (including an optional 'language') used for formatting.
            parent: A placeholder for potential hierarchical context (unused).
        
        Returns:
            A string containing the HTML markup for the code.
        """
        language = symbol.get_prop("language", "")
        inner = "\n".join([i.to_html() for i in inner])
        
        if language:
            return f'<code class="language-{language}">{inner}</code>'
        
        return f"<code>{inner}</code>"
    
    def verify(self, text: str) -> bool:
        """
        Checks if the provided text equals "code", ignoring case.
        
        Args:
            text: The string to verify.
        
        Returns:
            bool: True if text equals "code" (case-insensitive), otherwise False.
        """
        return text.lower() == "code"

class RST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Convert inner content to reStructuredText code format.
        
        Transforms the provided content into its RST representation based on the language
        specified in the symbol and whether the content spans multiple lines. When a language
        is indicated or the content contains newlines, the function formats the text as a
        code block using the appropriate directive and indentation. Otherwise, it returns the
        content as inline code, escaping backticks if present.
        
        Parameters:
            inner: Content to be converted, which may be a list of items (each supporting to_rst())
                   or a single item.
            symbol: An object used to retrieve properties (e.g., the programming language) for
                    formatting purposes.
            parent: Unused parameter included for interface consistency.
        
        Returns:
            str: The reStructuredText formatted representation of the code.
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