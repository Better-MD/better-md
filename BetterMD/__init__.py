from .elements import *
from .parse import Collection, HTMLParser, MDParser, RSTParser

def from_html(html:'str'):
    """
    Converts an HTML string into a Symbol object.
    
    Args:
        html: A string containing HTML content to convert.
    
    Returns:
        A Symbol object representing the parsed HTML.
    """
    return Symbol.from_html(html)

def from_md(md:'str'):
    """
    Converts a Markdown string into a Symbol.
    
    Args:
        md: A Markdown-formatted string.
    
    Returns:
        The Symbol object generated from the Markdown input.
    """
    return Symbol.from_md(md)