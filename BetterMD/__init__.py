from .elements import *
from .parse import Collection, HTMLParser, MDParser, RSTParser

def from_html(html:'str'):
    """
    Converts an HTML string into a Symbol.
    
    Given a string with HTML content, returns the corresponding Symbol object.
    """
    return Symbol.from_html(html)

def from_md(md:'str'):
    """
    Convert a Markdown formatted string into a Symbol object.
    
    Parses the provided Markdown text and returns the corresponding Symbol
    using the Symbol.from_md conversion method.
    
    Args:
        md (str): A string containing Markdown formatted text.
    
    Returns:
        Symbol: The Symbol object generated from the Markdown input.
    """
    return Symbol.from_md(md)