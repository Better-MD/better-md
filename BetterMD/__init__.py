from .elements import *
from .parse import Collection, HTMLParser, MDParser, RSTParser

def from_html(html:'str'):
    """
    Converts an HTML string to a Symbol object.
    
    This function processes the provided HTML content by calling the Symbol.from_html method and returns the resulting Symbol.
    
    Args:
        html: The HTML content to convert.
    
    Returns:
        The Symbol object corresponding to the input HTML.
    """
    return Symbol.from_html(html)

def from_md(md:'str'):
    """
    Converts a Markdown string into a Symbol instance.
    
    This function processes a Markdown-formatted string by invoking the
    Symbol.from_md method to generate a corresponding Symbol object.
    
    Args:
        md (str): The Markdown content to be converted.
    """
    return Symbol.from_md(md)