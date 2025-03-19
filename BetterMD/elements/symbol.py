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
        Automatically registers new subclasses in the symbol collection.
        
        This method adds the new subclass to the class-wide symbol collection and then
        delegates additional initialization to the superclass.
        """
        cls.collection.add_symbols(cls)
        super().__init_subclass__(**kwargs)

    def __init__(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=[], **props):
        """
        Initialize a new Symbol instance with optional styles, classes, inner symbols, and additional properties.
        
        Args:
            styles (dict[str, str]): CSS style definitions for the symbol.
            classes (list[str]): CSS class names for the symbol.
            inner (list[Symbol]): Initial child symbols to be assigned.
            **props: Additional properties to associate with the symbol.
        """
        self.styles = styles
        self.classes = classes
        self.children = list(inner) or []
        self.props = props


    def copy(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=None):
        """
        Return a copy of the symbol with merged styles and specified children.
        
        Merges the current symbol's styles into the provided styles dictionary so that the
        symbol's own styles override any overlapping keys. The resulting dictionary, along with
        the given list of class names and inner symbols (defaulting to an empty list if not provided),
        is used to create a new Symbol instance.
        
        Args:
            styles (dict[str, str]): Optional dictionary to merge with the symbol's styles.
            classes (list[str]): Optional list of class names for the new symbol.
            inner (list[Symbol], optional): Optional list of inner symbols; defaults to an empty list.
        
        Returns:
            Symbol: A new Symbol instance with the merged styles, specified classes, and inner symbols.
        """
        if inner == None:
            inner = []
        styles.update(self.styles)
        return Symbol(styles, classes, inner = inner)


    def set_parent(self, parent:'Symbol'):
        """
        Set the parent symbol for this instance and add it as a child of the parent.
        
        Args:
            parent: The Symbol instance to be assigned as the parent.
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
        Checks if a child symbol of a specified type exists.
        
        Iterates over the symbol's children and returns the first child that is an instance of the specified type.
        If no matching child is found, returns False.
        
        Args:
            child: The Symbol subclass to search for among the children.
        
        Returns:
            The first child instance matching the specified type, or False if none is found.
        """
        for e in self.children:
            if isinstance(e, child):
                return e

        return False

    def prepare(self, parent:'Symbol'):
        """
        Prepares the symbol by setting its parent and recursively preparing its children.
        
        Marks the symbol as prepared, assigns the given parent, and applies the same preparation process to every child symbol.
        
        Args:
            parent: The parent Symbol instance to be assigned to the current symbol.
        
        Returns:
            The prepared Symbol instance.
        """
        self.prepared = True
        self.parent = parent
        for symbol in self.children:
            symbol.prepare(self)

        return self

    def replace_child(self, old:'Symbol', new:'Symbol'):
        """
        Replaces an existing child symbol with a new one.
        
        Finds the index of the specified old child within the children list, removes it,
        and inserts the new symbol at the position immediately preceding the removed child's
        former index.
        
        Args:
            old: The child symbol to replace.
            new: The new child symbol to insert.
        
        Raises:
            ValueError: If the old child is not found among the children.
        """
        i = self.children.index(old)
        self.children.remove(old)

        self.children[i-1] = new


    def to_html(self, indent=1) -> 'str':
        """
        Converts the symbol and its children into an HTML representation.
        
        If the symbol's HTML attribute is an instance of CustomHTML, its own
        to_html method is called. Otherwise, an HTML tag is constructed with
        any associated CSS classes, inline styles, and additional properties.
        Child elements are formatted and indented based on the specified indent
        level. A self-closing tag is returned when no child content exists.
        
        Args:
            indent: The current indentation level for formatting nested child elements.
        
        Returns:
            The complete HTML string representation of the symbol.
        """
        if isinstance(self.html, CustomHTML):
            return self.html.to_html(self.children, self, self.parent)

        inner_HTML = f"\n{"    "*indent}".join([e.to_html(indent+1) if not (len(self.children) == 1 and self.children[0].html == "text") else e.to_html(0) for e in self.children])
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{inner_HTML}{"\n" if len(self.children) > 1 else ""}</{self.html}>" if inner_HTML else f" />"}"

    def to_md(self) -> 'str':
        """
        Generates a Markdown representation of the symbol and its children.
        
        If the symbol's md attribute is a CustomMarkdown instance, its to_md() method is invoked.
        Otherwise, the Markdown output is constructed by concatenating the symbol's md attribute
        with the Markdown representations of its child symbols. A newline character is appended
        if the nl attribute is set.
        """
        if isinstance(self.md, CustomMarkdown):
            return self.md.to_md(self.children, self, self.parent)

        inner_md = "".join([e.to_md() for e in self.children])
        return f"{self.md}{inner_md}" + ("\n" if self.nl else "")

    def to_rst(self) -> 'str':
        """
        Convert the symbol and its children to an RST string representation.
        
        If the symbol's "rst" attribute is an instance of CustomRst, the conversion is delegated to
        its "to_rst" method with the children, the symbol itself, and its parent. Otherwise, the
        method concatenates the symbol's "rst" attribute with the RST representations of its children,
        appending the "rst" attribute again and a newline.
        """
        if isinstance(self.rst, CustomRst):
            return self.rst.to_rst(self.children, self, self.parent)

        inner_rst = " ".join([e.to_rst() for e in self.children])
        return f"{self.rst}{inner_rst}{self.rst}\n"

    @classmethod
    def from_html(cls, text:'str') -> 'list[Symbol]':
        """
        Parses an HTML string into a list of Symbol instances.
        
        This class method uses the HTML parser to convert the input string into parsed elements,
        and then retrieves the corresponding Symbol for each element from the symbol collection.
        Each element is processed by invoking the symbol's parse method. An error is raised if a
        matching symbol cannot be found for any parsed element.
        
        Returns:
            list[Symbol]: A list of Symbol instances derived from the parsed HTML elements.
        """
        parsed = cls.html_parser.parse(text)
        return [cls.collection.find_symbol(elm['name'] , raise_errors=True).parse(elm) for elm in parsed]

    @classmethod
    def parse(cls, text:'ELEMENT') -> 'Symbol':
        """
        Parses a structured element into a Symbol instance.
        
        This class method transforms a dictionary representation of an element—either a text
        node (with type 'text') or an element node (identified by its 'name')—into a Symbol.
        It extracts CSS styles and classes from the element's attributes, recursively parses
        child elements, and passes any remaining attributes as properties.
        
        Args:
            text: A dictionary representing the element. Expected to include keys such as
                  'attributes' (with optional 'style' and 'class' entries), 'children' (a list
                  of nested element dictionaries), and 'type'. For text nodes, a 'content' key
                  is expected; for element nodes, a 'name' key is used.
                  
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
        Parses a Markdown string and returns the corresponding Symbol instance.
        
        This method uses the class-level Markdown parser to convert the input text into a
        structured representation. It then locates the appropriate symbol from the collection
        (using the parsed name, with errors raised if not found) and further processes the parsed
        data to create a new Symbol instance.
        
        Args:
            text: A Markdown formatted string representing the symbol's data.
        
        Returns:
            A Symbol instance constructed based on the parsed Markdown content.
        
        Raises:
            Exception: If a symbol with the parsed name is not found in the collection.
        """
        parsed = cls.md_parser.parse(text)
        return cls.collection.find_symbol(parsed['name'], raise_errors=True).parse(parsed)



    def get_prop(self, prop, default="") -> 'str':
        """
        Retrieves the value of a property from the symbol's properties.
        
        If the property is not found, returns the specified default value.
        
        Args:
            prop: The key of the property to retrieve.
            default: The value to return if the property key is absent (defaults to an empty string).
        
        Returns:
            The property value as a string, or the default value if the key is not found.
        """
        return self.props.get(prop, default)

    def set_prop(self, prop, value):
        self.props[prop] = value

    def __contains__(self, item):
        """
        Determines if a specified child symbol or type exists among the children.
        
        If the given item is callable (typically a type), the method returns True if any
        child is an instance of that type. Otherwise, it checks for direct membership in
        the list of children.
        
        Returns:
            bool: True if a matching child is found, False otherwise.
        """
        if callable(item):
            return any(isinstance(e, item) for e in self.children)
        return item in self.children
    
    def __str__(self):
        """
            Return a string representation of the symbol as an HTML element.
        
            The string includes the element's tag name along with any defined CSS classes,
            inline styles, and additional properties. It also appends the count of child symbols.
            """
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{"\n" if len(self.children) > 1 else ""}{len(self.children)}</{self.html}>"}"

    __repr__ = __str__