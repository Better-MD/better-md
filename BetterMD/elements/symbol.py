import typing as t

from ..markdown import CustomMarkdown
from ..html import CustomHTML
from ..rst import CustomRst
from ..parse import HTMLParser, MDParser, RSTParser, ELEMENT, TEXT, Collection

class Symbol:
    styles: 'dict[str, str]' = {}
    classes: 'list[str]' = []
    html: 't.Union[str, CustomHTML]' = ""
    props: 'dict[str, str]' = {}
    prop_list: 'list[str]' = []
    vars:'dict[str,str]' = {}
    children:'list[Symbol]' = []
    md: 't.Union[str, CustomMarkdown]' = ""
    rst: 't.Union[str, CustomRst]' = ""
    parent:'Symbol' = None
    prepared:'bool' = False
    nl:'bool' = False

    html_written_props = ""

    collection = Collection()
    html_parser = HTMLParser()
    md_parser = MDParser()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically registers a new symbol subclass in the global collection.
        
        This special method is called when a new subclass is defined. It adds the
        subclass to the collection by invoking its add_symbols method and then delegates
        further subclass initialization to the superclass.
        """
        cls.collection.add_symbols(cls)
        super().__init_subclass__(**kwargs)

    def __init__(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=[], **props):
        """
        Initialize a Symbol instance with optional styles, classes, children, and properties.
        
        This constructor sets up the symbol with provided CSS styles, class names, and a list
        of child Symbol instances (stored in the children attribute). Any additional keyword
        arguments are stored as properties.
            
        Args:
            styles (dict[str, str]): Optional mapping of CSS property names to values.
            classes (list[str]): Optional list of CSS class names.
            inner (list[Symbol]): Optional list of child Symbol instances.
            **props: Additional properties to be associated with the symbol.
        """
        self.styles = styles
        self.classes = classes
        self.children = list(inner) or []
        self.props = props


    def copy(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=None):
        """
        Creates a copy of the current symbol with merged styles, custom classes, and inner symbols.
        
        The provided styles dictionary is updated with the symbol's own styles so that any key in the
        original symbol takes precedence. The classes and inner parameters are used to set the new symbol's
        CSS classes and child symbols, with inner defaulting to an empty list if not provided.
        
        Args:
            styles: A dictionary of CSS styles to merge with the symbol's existing styles.
            classes: A list of CSS class names for the new symbol.
            inner: An optional list of child Symbol instances to include in the copy. Defaults to an empty list.
        
        Returns:
            A new Symbol instance with updated styles, classes, and inner symbols.
        """
        if inner == None:
            inner = []
        styles.update(self.styles)
        return Symbol(styles, classes, inner = inner)


    def set_parent(self, parent:'Symbol'):
        """
        Sets the parent of this symbol and registers it as a child.
        
        Assigns the provided Symbol instance as the parent of the current symbol and
        adds this symbol to the parent's list of children.
        """
        self.parent = parent
        self.parent.add_child(self)

    def change_parent(self, new_parent:'Symbol'):
        self.set_parent(new_parent)
        self.parent.remove_child(self)

    def add_child(self, symbol:'Symbol'):
        self.children.append(symbol)

    def remove_child(self, symbol:'Symbol'):
        self.children.remove(symbol)

    def has_child(self, child:'type[Symbol]'):
        """
        Checks if a child symbol of the specified type exists.
        
        Iterates over the symbol's children and returns the first instance that is of the given type.
        If no such child is found, returns False.
        
        Parameters:
            child: A subclass of Symbol to look for among the children.
        
        Returns:
            The first child that is an instance of the specified type, or False if none exists.
        """
        for e in self.children:
            if isinstance(e, child):
                return e

        return False

    def prepare(self, parent:'Symbol'):
        """
        Prepare the symbol and its children for processing.
        
        Marks the symbol as prepared, assigns the provided symbol as its parent, and
        recursively prepares each child by setting the current symbol as their parent.
        
        Args:
            parent: The new parent symbol for this symbol.
        
        Returns:
            The prepared symbol instance.
        """
        self.prepared = True
        self.parent = parent
        for symbol in self.children:
            symbol.prepare(self)

        return self

    def replace_child(self, old:'Symbol', new:'Symbol'):
        """
        Replaces a child Symbol with a new Symbol.
        
        Finds the first occurrence of the specified old child in the parent's children list,
        removes it, and assigns the new child to the position immediately preceding the removed
        child's original index. Note that if the old child is the first element, the new child
        will replace the last element.
        
        Args:
            old: The child Symbol instance to be replaced.
            new: The replacement Symbol instance.
        """
        i = self.children.index(old)
        self.children.remove(old)

        self.children[i-1] = new


    def to_html(self, indent=1) -> 'str':
        """
        Converts the symbol to an HTML string.
        
        Generates an HTML representation of the symbol, including its attributes and child
        elements. If the symbol's HTML attribute is an instance of a custom HTML handler, that
        handler’s conversion is used. Otherwise, an HTML tag is constructed with any associated
        CSS classes, inline styles, and additional properties, and its child symbols are rendered
        recursively. The indent parameter adjusts the indentation level for nested elements.
        
        Args:
            indent: The current indentation level for formatting nested elements (default is 1).
        
        Returns:
            A string containing the HTML representation of the symbol.
        """
        if isinstance(self.html, CustomHTML):
            return self.html.to_html(self.children, self, self.parent)

        inner_HTML = f"\n{"    "*indent}".join([e.to_html(indent+1) if not (len(self.children) == 1 and self.children[0].html == "text") else e.to_html(0) for e in self.children])
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{inner_HTML}{"\n" if len(self.children) > 1 else ""}</{self.html}>" if inner_HTML else f" />"}"

    def to_md(self) -> 'str':
        """
        Convert the symbol and its children to a Markdown string.
        
        If the symbol's Markdown attribute is a CustomMarkdown instance, its custom
        conversion method is used with the symbol's children, self, and parent.
        Otherwise, the base Markdown content is concatenated with the Markdown
        outputs of its children, and a newline is appended if the newline flag is set.
        
        Returns:
            A string containing the Markdown representation of the symbol.
        """
        if isinstance(self.md, CustomMarkdown):
            return self.md.to_md(self.children, self, self.parent)

        inner_md = "".join([e.to_md() for e in self.children])
        return f"{self.md}{inner_md}" + ("\n" if self.nl else "")

    def to_rst(self) -> 'str':
        """
        Converts the symbol and its children to a reStructuredText (RST) string.
        
        If the symbol's `rst` attribute is a CustomRst instance, the conversion is delegated to its
        `to_rst` method with the symbol’s children, itself, and its parent. Otherwise, the method
        concatenates the RST representations of its children, wrapping them with the symbol's `rst`
        string and appending a newline.
        """
        if isinstance(self.rst, CustomRst):
            return self.rst.to_rst(self.children, self, self.parent)

        inner_rst = " ".join([e.to_rst() for e in self.children])
        return f"{self.rst}{inner_rst}{self.rst}\n"

    @classmethod
    def from_html(cls, text:'str') -> 'list[Symbol]':
        """
        Parses an HTML string and returns a list of Symbol instances.
        
        This method utilizes the class-level HTML parser to convert the provided HTML text into a list of element dictionaries. For each element, it finds the corresponding Symbol from the collection (raising errors if not found) and parses it into a Symbol instance.
        
        Args:
            text: A string containing the HTML content to be parsed.
        
        Returns:
            A list of Symbol instances corresponding to the parsed HTML elements.
        """
        parsed = cls.html_parser.parse(text)
        return [cls.collection.find_symbol(elm['name'] , raise_errors=True).parse(elm) for elm in parsed]

    @classmethod
    def parse(cls, text:'ELEMENT') -> 'Symbol':
        """
        Parses an ELEMENT dictionary into a Symbol instance.
        
        Processes a structured dictionary representing an element by extracting inline
        styles from the "style" attribute and CSS class names from the "class" attribute.
        Recursively parses child elements and text nodes via the symbol collection,
        passing remaining attributes to the Symbol constructor.
        
        Args:
            text: A dictionary representing an ELEMENT with keys such as "attributes",
                  "children", "type", "name", and "content".
        
        Returns:
            A Symbol instance corresponding to the parsed element.
        """
        def handle_element(element:'ELEMENT|TEXT') -> 'Symbol':
            if element['type'] == 'text':
                text = cls.collection.find_symbol("text", raise_errors=True)
                assert text is not None, "`collection.find_symbol` is broken"

                return text(element['content'])

            symbol_cls = cls.collection.find_symbol(element['name'], raise_errors=True)
            assert symbol_cls is not None, "`collection.find_symbol` is broken"

            return symbol_cls.parse(element)

        styles = {s.split(":")[0]: s.split(":")[1] for s in text["attributes"].pop("style", "").split(";") if ":" in s}
        classes = list(filter(lambda c: bool(c), text["attributes"].pop("class", "").split(" ")))

        return cls(styles, classes, inner=[handle_element(elm) for elm in text["children"]], **text["attributes"])

    @classmethod
    def from_md(cls, text: str) -> 'Symbol':
        """
        Creates a Symbol instance from a Markdown string.
        
        Parses the provided Markdown text using the class's Markdown parser to produce an
        intermediate representation of the symbol. It then uses the 'name' field from the parsed
        data to look up the corresponding symbol in the collection and constructs a Symbol instance
        by parsing the intermediate representation.
        
        Args:
            text: A Markdown formatted string representing a symbol element.
        
        Returns:
            A Symbol instance constructed from the parsed Markdown data.
        """
        parsed = cls.md_parser.parse(text)
        return cls.collection.find_symbol(parsed['name'], raise_errors=True).parse(parsed)



    def get_prop(self, prop, default="") -> 'str':
        """
        Retrieves a property value from the symbol's properties.
        
        Looks up the specified key in the symbol's properties dictionary and returns its
        value. If the key is not found, the provided default value is returned.
        
        Args:
            prop: The name of the property to retrieve.
            default: The fallback value if the property key is absent (defaults to an empty string).
        
        Returns:
            The value associated with the key as a string.
        """
        return self.props.get(prop, default)

    def set_prop(self, prop, value):
        self.props[prop] = value

    def __contains__(self, item):
        """
        Determines whether a child symbol is present based on the specified condition.
        
        If the given item is callable (typically a type), the method returns True if
        any child is an instance of that callable. Otherwise, it performs a direct
        membership test against the children.
        
        Args:
            item: A child symbol instance or a callable (usually a type) to check
                against each child.
        
        Returns:
            bool: True if the condition is met; otherwise, False.
        """
        if callable(item):
            return any(isinstance(e, item) for e in self.children)
        return item in self.children
    
    def __str__(self):
        """
        Return a string representation of the symbol as an HTML element.
        
        Formats the symbol into an HTML-like string that includes its tag name and conditionally
        adds CSS classes, inline styles, and additional properties. Also indicates the number of
        child symbols, with extra line breaks when more than one child is present.
        """
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{"\n" if len(self.children) > 1 else ""}{len(self.children)}</{self.html}>"}"

    __repr__ = __str__