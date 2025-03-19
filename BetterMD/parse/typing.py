import typing as t

class TEXT(t.TypedDict):
    type: t.Literal["text"]
    content: str
    name: t.Literal["text"]

class ELEMENT(t.TypedDict):
    type: 't.Literal["element"]'
    name: 'str'
    attributes: 'dict[str, str]'
    children: 'list[t.Union[ELEMENT, TEXT]]'

@t.runtime_checkable
class Parser(t.Protocol):
    def parse(self, html:'str') -> 'list[ELEMENT]': """
Parse HTML markup into a list of structured HTML elements.

This method converts the given HTML string into a hierarchical list of ELEMENT
objects representing both HTML elements and text nodes.

Args:
    html: The HTML content to parse.

Returns:
    A list of ELEMENT objects representing the parsed HTML structure.
"""
...