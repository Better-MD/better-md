from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..html import CustomHTML


# This is not equivelant to the html span or p tags but instead just raw text

class Text(Symbol):
    md = "text"
    html = "text"
    rst = "text"

    def __init__(self, text:str, **props):
        """
        Initializes a Text instance with the provided text and additional properties.
        
        Args:
            text (str): The content of the text element.
            **props: Additional keyword arguments passed to the parent Symbol class.
        """
        self.text = text
        return super().__init__(**props)

    def to_html(self, indent=0, parent=None):
        """
        Return the text content as an HTML-formatted string with indentation.
        
        Prefixes the text with repeated four-space blocks corresponding to the provided
        indentation level. The parent parameter is ignored.
            
        Args:
            indent (int, optional): The number of indentation levels to apply. Defaults to 0.
            parent: Optional parameter maintained for interface consistency; not used.
        
        Returns:
            str: The indented HTML-formatted text.
        """
        return f"{'    '*indent}{self.text}"

    def to_md(self):
        """
        Return the text as a Markdown string.
        
        Returns:
            str: The original text.
        """
        return self.text
    
    def to_rst(self):
        """
        Return the text content for reStructuredText.
        
        Returns:
            str: The text content as a reStructuredText string.
        """
        return self.text
