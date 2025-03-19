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
        Initialize a Text instance with the provided content.
        
        Assigns the given text to the instance and forwards any additional keyword
        arguments to the parent Symbol constructor.
        
        Args:
            text: The content to be rendered.
            **props: Additional properties for further configuration.
        """
        self.text = text
        return super().__init__(**props)

    def to_html(self, indent=0, parent=None):
        """
        Return the HTML representation of the text with applied indentation.
        
        This method formats the stored text by prepending a specified number of four-space
        indentation levels. The 'parent' parameter is accepted for interface compatibility
        but is currently not used.
        
        Args:
            indent: Number of indentation levels to apply (each level equals four spaces).
            parent: Reserved for future use.
            
        Returns:
            A string containing the indented text.
        """
        return f"{'    '*indent}{self.text}"

    def to_md(self):
        """
        Return the text content as Markdown.
        
        Returns:
            str: The original text.
        """
        return self.text
    
    def to_rst(self):
        """
        Returns the text as reStructuredText.
        
        This method returns the raw text stored in the instance, intended for use in reStructuredText output.
        """
        return self.text
