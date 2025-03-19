from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..html import CustomHTML


# This is not equivelant to the html span or p tags but instead just raw text

class Text(Symbol):
    md = "text"
    html = "text"
    rst = "text"

    def __init__(self, text:str, **props):
        """Initialize a Text instance with the specified content.
        
        Args:
            text (str): The text content to be assigned to the instance.
            **props: Additional keyword arguments forwarded to the parent initializer.
        """
        self.text = text
        return super().__init__(**props)

    def to_html(self, indent=0, parent=None):
        """
        Return the text formatted with optional indentation for HTML output.
        
        The function prefixes the text attribute with four spaces per indent level.
        The parent parameter is not used.
        """
        return f"{'    '*indent}{self.text}"

    def to_md(self):
        """
        Return the text attribute as Markdown output.
        
        This method returns the stored text without modification, making it suitable for Markdown rendering.
        """
        return self.text
    
    def to_rst(self):
        """
        Return the text formatted as reStructuredText.
        
        Returns:
            str: The text attribute, suitable for reStructuredText rendering.
        """
        return self.text
