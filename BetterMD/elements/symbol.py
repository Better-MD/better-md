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
        Automatically registers a new subclass with the symbol collection.
        
        This method is invoked when a subclass is defined. It adds the subclass to the
        class-level collection via the add_symbols method and passes any additional
        keyword arguments to the superclass's __init_subclass__.
        """
        cls.collection.add_symbols(cls)
        super().__init_subclass__(**kwargs)

    def __init__(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=[], **props):
        """
        Initialize a Symbol instance with optional styles, classes, children, and additional properties.
        
        Args:
            styles: A dictionary mapping CSS property names to values.
            classes: A list of CSS class names.
            inner: A list of child Symbol instances.
            **props: Additional properties to assign to the symbol.
        """
        self.styles = styles
        self.classes = classes
        self.children = list(inner) or []
        self.props = props


    def copy(self, styles:'dict[str,str]'={}, classes:'list[str]'=[], inner:'list[Symbol]'=None):
        """
        Create a copy of the symbol with merged styles, specified classes, and inner symbols.
        
        The provided styles dictionary is updated with the symbol's current styles. If no inner symbols are given, an empty list is used. Returns a new Symbol instance with the combined attributes.
        """
        if inner == None:
            inner = []
        styles.update(self.styles)
        return Symbol(styles, classes, inner = inner)


    def set_parent(self, parent:'Symbol'):
        """
        Sets the parent for this symbol and registers it as a child of that parent.
        
        Args:
            parent: The Symbol instance to assign as this symbol's parent.
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
        Check if the symbol has a child of the specified type.
        
        Iterates over the symbol's children and returns the first instance that is a subclass of the provided type. If no such child exists, returns False.
        
        Args:
            child: The Symbol subclass type to search for among the children.
        
        Returns:
            The first matching Symbol instance if found; otherwise, False.
        """
        for e in self.children:
            if isinstance(e, child):
                return e

        return False

    def prepare(self, parent:'Symbol'):
        """
        Prepare the symbol and its children for processing.
        
        Marks the symbol as prepared, assigns the given parent as its parent, and
        recursively prepares each child symbol by setting their parent to the current symbol.
        
        Args:
            parent: The parent symbol to associate with this symbol.
        
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
        Replace an existing child symbol with a new symbol in the children list.
        
        This function locates the first occurrence of the specified old symbol among the children,
        removes it from the list, and then assigns the new symbol into the position immediately preceding
        the old symbol’s original index. Note that if the old symbol is at the start of the list (index 0),
        the new symbol will replace the last element due to negative indexing.
        
        Args:
            old: The child symbol to be replaced.
            new: The symbol that will take the place of the old child.
        
        Raises:
            ValueError: If the old symbol is not found among the children.
        """
        i = self.children.index(old)
        self.children.remove(old)

        self.children[i-1] = new


    def to_html(self, indent=1) -> 'str':
        """
        Generates the HTML representation of the symbol and its children.
        
        If the symbol’s HTML attribute is a CustomHTML instance, the method delegates
        the conversion to its to_html method. Otherwise, it constructs an HTML tag using
        the symbol’s tag name, and dynamically includes attributes from its classes,
        styles, and properties. Child symbols are recursively converted to HTML with
        indentation controlled by the indent parameter; a self-closing tag is returned if
        no inner content is generated.
        
        Args:
            indent (int): The current indentation level for formatting nested HTML.
        
        Returns:
            str: The HTML string representation of the symbol.
        """
        if isinstance(self.html, CustomHTML):
            return self.html.to_html(self.children, self, self.parent)

        inner_HTML = f"\n{"    "*indent}".join([e.to_html(indent+1) if not (len(self.children) == 1 and self.children[0].html == "text") else e.to_html(0) for e in self.children])
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{inner_HTML}{"\n" if len(self.children) > 1 else ""}</{self.html}>" if inner_HTML else f" />"}"

    def to_md(self) -> 'str':
        """
        Converts the symbol to a Markdown formatted string.
        
        If the symbol's markdown attribute is a CustomMarkdown instance, its custom conversion method
        is used with the symbol's children, the symbol itself, and its parent. Otherwise, this method
        concatenates the symbol's markdown content with the Markdown representations of its child symbols,
        appending a newline if the symbol's 'nl' flag is set.
        """
        if isinstance(self.md, CustomMarkdown):
            return self.md.to_md(self.children, self, self.parent)

        inner_md = "".join([e.to_md() for e in self.children])
        return f"{self.md}{inner_md}" + ("\n" if self.nl else "")

    def to_rst(self) -> 'str':
        """
        Converts the symbol and its children to reStructuredText format.
        
        If the symbol’s rst attribute is a CustomRst instance, its to_rst() method is
        called with the symbol’s children, the symbol itself, and its parent. Otherwise,
        the method assembles the RST representation by concatenating the symbol’s rst
        value, a space-separated string of its children's RST representations, and the
        rst value again, followed by a newline.
        
        Returns:
            str: The complete reStructuredText representation of the symbol.
        """
        if isinstance(self.rst, CustomRst):
            return self.rst.to_rst(self.children, self, self.parent)

        inner_rst = " ".join([e.to_rst() for e in self.children])
        return f"{self.rst}{inner_rst}{self.rst}\n"

    @classmethod
    def from_html(cls, text:'str') -> 'list[Symbol]':
        """
        Parses HTML content and returns a list of Symbol instances.
        
        This class method uses the class's HTML parser to transform the input HTML text into a list
        of element dictionaries. For each element, it retrieves the corresponding symbol from the
        collection by name and then parses the element into a Symbol instance. An error is raised
        if no matching symbol is found.
          
        Args:
            text: A string containing HTML content.
          
        Returns:
            A list of Symbol instances generated from the parsed HTML elements.
        """
        parsed = cls.html_parser.parse(text)
        return [cls.collection.find_symbol(elm['name'] , raise_errors=True).parse(elm) for elm in parsed]

    @classmethod
    def parse(cls, text:'ELEMENT') -> 'Symbol':
        """
        Parses an element representation into a Symbol instance.
        
        This class method converts a structured element—provided as a dictionary containing keys
        like "attributes", "children", "name", and "type"—into a corresponding Symbol. It extracts
        inline CSS styles and class names from the element's attributes and recursively processes
        its children. For text nodes (where the type is "text"), the method uses the designated
        text symbol from the collection.
        
        Args:
            text: A dictionary representing the element to be parsed.
        
        Returns:
            A Symbol instance corresponding to the parsed element and its nested children.
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
        Parses Markdown text into a Symbol instance.
        
        This class method converts the input Markdown into a structured form using the
        Markdown parser, then retrieves and instantiates the corresponding Symbol from
        the collection using the parsed symbol name.
        
        Args:
            text: Markdown formatted text.
        
        Returns:
            A Symbol instance representing the parsed Markdown content.
        """
        parsed = cls.md_parser.parse(text)
        return cls.collection.find_symbol(parsed['name'], raise_errors=True).parse(parsed)



    def get_prop(self, prop, default="") -> 'str':
        """
        Retrieves a property value from the symbol's properties.
        
        Looks up the specified key in the properties dictionary and returns its value if found;
        otherwise, returns the provided default value.
        
        Args:
            prop: The property key to retrieve.
            default: Value to return if the property is not present (defaults to an empty string).
        
        Returns:
            The property value as a string.
        """
        return self.props.get(prop, default)

    def set_prop(self, prop, value):
        self.props[prop] = value

    def __contains__(self, item):
        """
        Checks if a given item or type exists among the symbol's children.
        
        If the provided item is callable (typically a type), the method returns True
        if any child is an instance of that type; otherwise, it performs a standard
        membership check in the children list.
        """
        if callable(item):
            return any(isinstance(e, item) for e in self.children)
        return item in self.children
    
    def __str__(self):
        """Return an HTML-like string representation of the symbol.
        
        Constructs a string that mimics an HTML element using the symbol's tag name and,
        if present, includes attributes for CSS classes, inline styles, and additional properties.
        When the symbol has more than one child, extra formatting with newlines is applied and
        the count of child symbols is displayed between the opening and closing tags.
        """
        return f"<{self.html}{" " if self.styles or self.classes or self.props else ""}{f"class={'"'}{' '.join(self.classes) or ''}{'"'}" if self.classes else ""}{" " if (self.styles or self.classes) and self.props else ""}{f"style={'"'}{' '.join([f'{k}:{v}' for k,v in self.styles.items()]) or ""}{'"'}" if self.styles else ""}{" " if (self.styles or self.classes) and self.props else ""}{' '.join([f'{k}={'"'}{v}{'"'}' if v != "" else f'{k}' for k,v in self.props.items()])}{f">{"\n" if len(self.children) > 1 else ""}{"\n" if len(self.children) > 1 else ""}{len(self.children)}</{self.html}>"}"

    __repr__ = __str__