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
    def parse(self, html:'str') -> 'list[ELEMENT]': """Parse an HTML string into a list of element structures.

Parses the provided HTML markup and returns a list of ELEMENT dictionaries.
Each dictionary represents an HTML element with its tag name, attributes, and child
nodes, conforming to the ELEMENT TypedDict schema.

Args:
    html: A string containing the HTML markup to parse.

Returns:
    A list of ELEMENT dictionaries representing the parsed HTML structure.
"""
...