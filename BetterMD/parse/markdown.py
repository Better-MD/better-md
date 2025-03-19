import re
import typing as t
from .typing import ELEMENT, TEXT
import threading as th

class MDParser:

    top_level_tags = {
        "blockquote": r"^> (.+)$", # Blockquote
        "br": r"\n\n", # Br
        "code": r"^```([A-Za-z]*)[^.](?:([^`]*)[^.])?```$", # Code block

        "h": r"^(#{1,6})(?: (.*))?$",

        "hr": r"^---+$", # Hr

        "ul" : r"^([ |	]*)(?:-|\+|\*)(?: (.*))?$", # Ul Li
        "ol" : r"^([ |	]*)(\d)\.(?: (.*))?$", # Ol Li

        "tr": r"^\|(?:[^|\n]+\|)+$",  # tr - must start and end with | and have at least one |
        "thead": r"^\|(?::?-+:?\|)+$", # thead / tbody

        "title": r"^title: .+$", # Title
    }

    def __init__(self):
        """
        Initializes the MDParser instance.
        
        Sets up the parser to a clean initial state by calling reset().
        """
        self.reset()

    def reset(self):
        """
        Resets the parser's internal state.
        
        Clears the document object model (DOM), text buffer, list stack, and DOM stack to prepare
        for a new markdown parsing operation.
        """
        self.dom = []
        self.buffer = ''
        self.list_stack = []
        self.dom_stack = []

    def create_element(self, name:'str', attrs:'dict[str, str]'=None, children:'list[ELEMENT|TEXT]'=None) -> 'ELEMENT':
        """
        Creates a new element node for the Markdown DOM.
        
        Constructs and returns a dictionary representing an element with a given tag name,
        optional attributes, and child nodes. If the attributes or children are not provided,
        they default to an empty dictionary or list, respectively.
        
        Args:
            name (str): The name of the element.
            attrs (dict[str, str], optional): A mapping of attribute names to their values.
            children (list[ELEMENT|TEXT], optional): A list of child nodes for the element.
        
        Returns:
            ELEMENT: A dictionary representing the constructed element node.
        """
        if children is None:
            children = []

        if attrs is None:
            attrs = {}

        return {
            "type": "element",
            "name": name,
            "attributes": attrs,
            "children": children
        }

    def create_text(self, content:'str') -> 'TEXT':
        """
        Creates a text node element.
        
        Constructs and returns a dictionary representing a text node for the DOM. The
        element includes its type, name, and provided text content.
        
        Args:
            content: The text content for the node.
        
        Returns:
            A dictionary with keys "type", "content", and "name" representing the text node.
        """
        return {
            "type": "text",
            "content": content,
            "name": "text"
        }
    
    def end_block(self):
        # Create paragraph from buffered text
        """
        Finalizes the current text block as a paragraph.
        
        If there is any buffered text, the method trims whitespace and, if non-empty,
        creates a paragraph element with the text, appending it to the document model.
        Finally, it clears the text buffer.
        """
        if self.buffer:
            text = self.buffer.strip()
            if text:
                para = self.create_element("p", children=[self.create_text(text)])
                self.dom.append(para)
            self.buffer = ''

    def start_block(self):
        """
        Placeholder for starting a new block.
        
        This method currently performs no action and is reserved for future use.
        """
        pass

    def handle_blockquote(self, text: 'list[str]', i):
        """
        Processes blockquote lines from the Markdown text and appends the resulting element to the DOM.
        
        This method scans the list of Markdown lines beginning at index i, removing 
        leading blockquote markers (">" or "> ") and joining consecutive lines into paragraphs.
        Empty lines trigger paragraph breaks. Lines that do not match any known top-level tag
        are treated as continuations of the blockquote. The accumulated text is then recursively
        parsed, and the resulting structure is set as the children of a new blockquote element,
        which is added to the DOM.
        
        Args:
            text: A list of Markdown lines.
            i: The starting index for blockquote processing.
        
        Returns:
            The number of lines consumed during the blockquote processing.
        """
        elm = self.create_element("blockquote")
        new_text = []
        current_line = []

        for line in text[i:]:
            if re.match(self.top_level_tags["blockquote"], line):
                # Remove blockquote marker and add to current line
                content = line.removeprefix("> ").removeprefix(">").strip()
                if content:
                    current_line.append(content)
            elif line.strip() == "":
                # Empty line marks paragraph break
                if current_line:
                    new_text.append(" ".join(current_line))
                    new_text.append("")
                    current_line = []
            elif not any(re.match(pattern, line) for pattern in self.top_level_tags.values()):
                # Continuation of blockquote without marker
                current_line.append(line.strip())
            else:
                break

        if current_line:
            new_text.append(" ".join(current_line))

        # Parse blockquote content recursively
        elm["children"] = MDParser().parse("\n".join(new_text))
        self.dom.append(elm)
        
        return len(new_text) - 1

    def handle_code(self, text: 'list[str]'):
        """
        Processes a Markdown code block and appends it to the DOM.
        
        Finalizes any pending text block, extracts the code block's language and content
        using a regex pattern, and creates a preformatted element containing a code child.
        The constructed element is then appended to the document model.
        
        Args:
            text: A list of strings representing the lines of a Markdown code block.
        
        Returns:
            The relative index of the closing code block delimiter within the joined text.
        
        Raises:
            AssertionError: If the provided text does not match the expected code block pattern.
        """
        self.end_block()
        match = re.match(self.top_level_tags["code"], "\n".join(text))
        assert match is not None, "Code block not found"

        lang = match.group(1)
        content = match.group(2)

        elm = self.create_element("pre", children=[self.create_element("code", {"language": lang}, [self.create_text(content)])])
        self.dom.append(elm)

        return "\n".join(text)["\n".join(text).index("```"):].index("```")


    def handle_br(self, text: 'list[str]'):
        """
        Finalizes the current block and inserts a line break if two consecutive blank lines are found.
        
        This function ends any ongoing text block and examines the first two entries in the provided
        list. If both are empty strings, it appends a break element to the DOM to represent a line break
        and returns 1. Otherwise, it returns 0.
        """
        self.end_block()
        if text[0] == "" and text[1] == "":
            self.dom.append(self.create_element("br", {}))
            return 1
        return 0

    def handle_h(self, line: 'str'):
        """
        Processes a Markdown header line and appends a corresponding header element to the DOM.
        
        This method finalizes the current text block and uses a regular expression to
        determine the header level (based on the number of '#' characters) and extract
        the header content. It then creates an HTML header element (e.g., h1, h2) and appends
        it to the DOM.
        
        Args:
            line: A Markdown header line (e.g., "# Header") to be processed.
        
        Raises:
            AssertionError: If the provided line does not match the expected header format.
        """
        self.end_block()
        match = re.match(self.top_level_tags["h"], line)
        assert match is not None, "Header not found"

        level = len(match.group(1))
        content = match.group(2)

        self.dom.append(self.create_element(f"h{level}", children=[self.create_text(content)]))

    def handle_hr(self, line: 'str'):
        """
        Processes a horizontal rule.
        
        Finalizes the current text block and appends a horizontal rule element to the document.
        """
        self.end_block()
        self.dom.append(self.create_element("hr", {}))

    def handle_text(self, line: 'str'):
        # Don't create text nodes for empty lines
        """
        Processes a Markdown text line for paragraph buffering.
        
        If the line is empty or contains only whitespace, it invokes the line break handler.
        Otherwise, the line is appended to the internal buffer for later paragraph creation.
        """
        if not line.strip():
            self.handle_br(line)
            return

        # Buffer text content for paragraph handling
        if self.buffer:
            self.buffer += '\n' + line
        else:
            self.buffer = line

    def handle_list(self, text: 'list[str]', i: int, indent_level: int = 0) -> int:
        """
        Parses Markdown list items and appends the constructed list to the DOM.
        
        Starting from the provided index in a list of Markdown lines, this method identifies
        whether an ordered or unordered list is present. It processes each list item, handles
        nested lists recursively based on indentation, and converts list items into corresponding
        DOM elements. The method updates the DOM with the parsed list and returns the number
        of lines processed.
          
        Parameters:
            text: A list of strings representing the Markdown content.
            i: The starting index from which to begin parsing list items.
            indent_level: The current indentation level to determine list nesting (default is 0).
        
        Returns:
            The number of lines processed during the list parsing.
        """
        if re.match(self.top_level_tags["ul"], text[i]):
            list_elm = self.create_element("ul")
            list_pattern = self.top_level_tags["ul"]
        elif re.match(self.top_level_tags["ol"], text[i]):
            list_elm = self.create_element("ol")
            list_pattern = self.top_level_tags["ol"]
        else:
            return 0

        current_item = []
        lines_processed = 0
        
        while i + lines_processed < len(text):
            line = text[i + lines_processed]
            
            if not line.strip():
                if current_item:
                    # Empty line in list item - treat as paragraph break
                    current_item.append("")
                lines_processed += 1
                continue

            list_match = re.match(list_pattern, line)
            if list_match:
                indent = len(list_match.group(1))
                
                if indent < indent_level:
                    # End of current list level
                    break
                elif indent > indent_level:
                    # Nested list
                    nested_lines = lines_processed + self.handle_list(text[i + lines_processed:], 0, indent)
                    lines_processed += nested_lines
                    continue
                
                # Add previous item if exists
                if current_item:
                    content = " ".join(current_item).strip()
                    if content:
                        list_elm["children"].append(
                            self.create_element("li", children=[self.create_text(content)])
                        )
                
                # Start new item
                current_item = [list_match.group(2).strip()]
                
            elif not any(re.match(pattern, line) for pattern in self.top_level_tags.values()):
                # Continuation of list item
                current_item.append(line.strip())
            else:
                break
                
            lines_processed += 1

        # Add final item
        if current_item:
            content = " ".join(current_item).strip()
            if content:
                list_elm["children"].append(
                    self.create_element("li", children=[self.create_text(content)])
                )

        self.dom.append(list_elm)
        return lines_processed

    def handle_table(self, text: 'list[str]', i: int) -> int:
        # First check if this is actually a table
        # A proper table needs at least two rows (header and separator)
        """
        Parses a Markdown table from the given lines and appends its HTML structure to the DOM.
        
        If a valid table is detected (requiring a header row and its corresponding separator), this method processes subsequent table rows to build header (thead) and body (tbody) sections. If the expected table format is not found, it treats the line as regular text instead.
        
        Args:
            text: A list of Markdown lines.
            i: The starting index in the text list where the table is expected.
        
        Returns:
            The number of lines processed for the table.
        """
        if i + 1 >= len(text) or not re.match(self.top_level_tags["thead"], text[i + 1]):
            # Not a table, treat as regular text
            self.handle_text(text[i])
            return 1
        
        lines_processed = 0
        table = self.create_element("table")
        thead = self.create_element("thead")
        tbody = self.create_element("tbody")
        current_section = thead
        
        while i + lines_processed < len(text):
            line = text[i + lines_processed]
            
            if not line.strip():
                break
                
            if re.match(self.top_level_tags["thead"], line):
                # Alignment row - skip it but switch to tbody
                current_section = tbody
                lines_processed += 1
                continue
                
            if re.match(self.top_level_tags["tr"], line):
                # Process table row
                row = self.create_element("tr")
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                
                for cell in cells:
                    if current_section == thead:
                        cell_type = "th"
                    else:
                        cell_type = "td"
                        
                    row["children"].append(
                        self.create_element(cell_type, children=[self.create_text(cell.strip())])
                    )
                    
                current_section["children"].append(row)
                lines_processed += 1
            else:
                break

        if thead["children"]:
            table["children"].append(thead)
        if tbody["children"]:
            table["children"].append(tbody)
            
        self.dom.append(table)
        return lines_processed
    
    def handle_title(self, line: 'str'):
        """
        Process a Markdown title line and set the document head element.
        
        Finalizes any open text block, validates that the line matches the expected title
        pattern, and extracts the title content. A head element is then created with a nested
        title element containing the extracted text.
        
        Args:
            line: A Markdown-formatted string representing the document title.
        
        Raises:
            AssertionError: If the title pattern is not found in the input line.
        """
        self.end_block()
        match = re.match(self.top_level_tags["title"], line)
        assert match is not None, "Title not found"

        title = match.group(1)
        self.head = self.create_element("head", children=[self.create_element("title", children=[self.create_text(title)])])

    def parse(self, markdown: 'str') -> 'ELEMENT':
        """
        Parses Markdown text into an HTML DOM structure.
        
        This method resets the internal parser state and processes the provided Markdown
        text line by line, invoking specialized handlers for block-level elements such as
        headers, blockquotes, code blocks, horizontal rules, lists, tables, titles, and line
        breaks. Regular text lines are buffered into paragraphs until a block boundary is
        encountered. The final result is a DOM element representing an HTML document with
        a head and body containing the parsed content.
        
        Args:
            markdown: A string containing Markdown-formatted text.
        
        Returns:
            An element representing the HTML structure.
        """
        self.reset()
        lines = markdown.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()  # Strip whitespace from each line

            # Empty line ends current block
            if not line:
                self.end_block()
                i += 1
                continue

            # Check for block-level elements
            if re.search(self.top_level_tags["h"], line):
                self.end_block()
                self.handle_h(line)
                i += 1
                continue
            
            elif re.search(self.top_level_tags["blockquote"], line):
                self.end_block()
                lines_processed = self.handle_blockquote(lines, i)
                i += lines_processed + 1
                continue
            
            elif re.search(self.top_level_tags["code"], "\n".join(lines[i:])):
                self.end_block()
                lines_processed = self.handle_code(lines[i:])
                i += lines_processed + 1
                continue
            
            elif re.search(self.top_level_tags["h"], line):
                self.end_block()
                self.handle_h(line)
                i += 1
                continue
            
            elif re.search(self.top_level_tags["hr"], line):
                self.end_block()
                self.handle_hr(line)
                i += 1
                continue
            
            elif re.search(self.top_level_tags["ul"], line) or re.search(self.top_level_tags["ol"], line):
                self.end_block()
                lines_processed = self.handle_list(lines, i)
                i += lines_processed
                continue
            
            elif re.search(self.top_level_tags["tr"], line):
                self.end_block()
                lines_processed = self.handle_table(lines, i)
                i += lines_processed
                continue
            
            elif re.search(self.top_level_tags["title"], line):
                self.end_block()
                self.handle_title(line)
                i += 1
                continue

            elif re.search(self.top_level_tags["br"], line):
                self.end_block()
                lines_processed = self.handle_br(lines[i:])
                i += lines_processed
                continue
            
            else:
                # Regular text gets buffered for paragraph handling
                self.handle_text(line)
                i += 1

        # End any remaining block
        self.end_block()

        head = self.create_element("head") or self.head
        body = self.create_element("body", children=self.dom)

        return self.create_element("html", children=[head, body])