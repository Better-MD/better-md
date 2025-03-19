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
Parses an HTML string into a list of ELEMENT objects.

Args:
    html: A string containing HTML-like data to be parsed.

Returns:
    A list of ELEMENT objects representing the hierarchical structure of the HTML.
"""
...