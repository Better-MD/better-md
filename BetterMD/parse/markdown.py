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
        Initialize the Markdown parser.
        
        Calls reset() to initialize the parser's internal state for a new parsing operation.
        """
        self.reset()

    def reset(self):
        """Reset the parser's internal state.
        
        Clears the document structure, text buffer, and stacks used for lists and DOM
        elements to prepare the parser for a new operation.
        """
        self.dom = []
        self.buffer = ''
        self.list_stack = []
        self.dom_stack = []

    def create_element(self, name:'str', attrs:'dict[str, str]'=None, children:'list[ELEMENT|TEXT]'=None) -> 'ELEMENT':
        """
        Creates a structured element dictionary for a DOM node.
        
        Constructs a dictionary representing an element with a specified tag name,
        attributes, and children. If no attributes or children are provided, they
        default to an empty dictionary or list, respectively.
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
        Creates a text element.
        
        Returns a dictionary representing a text node with the specified content.
        The returned element always includes the keys "type", set to "text", "content",
        carrying the provided text value, and "name", also set to "text".
        """
        return {
            "type": "text",
            "content": content,
            "name": "text"
        }
    
    def end_block(self):
        # Create paragraph from buffered text
        """
        Finalizes the buffered text into a paragraph element.
        
        If the internal buffer contains text, the method strips it and, if non-empty, creates a
        paragraph element with the text and appends it to the DOM. After processing, the buffer is cleared.
        """
        if self.buffer:
            text = self.buffer.strip()
            if text:
                para = self.create_element("p", children=[self.create_text(text)])
                self.dom.append(para)
            self.buffer = ''

    def start_block(self):
        """
        Placeholder method for starting a new block.
        
        This method is currently a no-op and may be extended in the future.
        """
        pass

    def handle_blockquote(self, text: 'list[str]', i):
        """
        Process a blockquote section in Markdown text.
        
        Scans the list of Markdown lines starting from the given index to extract the full
        blockquote content. The function removes blockquote markers, handles paragraph
        breaks on empty lines, and accepts continuation lines without explicit markers.
        It recursively parses the accumulated text into a blockquote element and appends
        it to the document model.
        
        Args:
            text: A list of Markdown lines.
            i: The starting index from which to process the blockquote.
        
        Returns:
            An integer indicating the number of lines consumed as part of the blockquote.
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
        Extracts and processes a code block from Markdown text lines.
        
        Finalizes any pending text block, then uses a regular expression to match and extract
        the language identifier and code content from the joined text lines. It wraps the code
        within a <code> element (annotated with the language) nested inside a <pre> element and
        appends this structure to the DOM. Returns the character offset from the opening to the
        closing code fence within the joined text.
            
        Args:
            text (list[str]): Markdown lines representing the code block.
            
        Returns:
            int: The offset from the opening code fence to the closing code fence.
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
        Handles Markdown line breaks by appending a <br> element if two empty lines are encountered.
        
        Finalizes the current text block and checks the first two lines of the provided markdown
        input. If both lines are empty, a <br> element is appended to the document model and
        the method returns 1, indicating that one line was processed. Otherwise, it returns 0.
          
        Args:
            text: A list of markdown lines; the first two lines are inspected for empty strings.
        """
        self.end_block()
        if text[0] == "" and text[1] == "":
            self.dom.append(self.create_element("br", {}))
            return 1
        return 0

    def handle_h(self, line: 'str'):
        """
        Process a Markdown header line and append it to the DOM.
        
        Ends any active text block, parses the line to determine the header level based on the 
        number of '#' characters, and extracts the header text. A header element (e.g., <h1>, <h2>) 
        is then created with the extracted content and added to the DOM. An assertion error is raised 
        if the line does not match the expected header format.
        
        Args:
            line: A Markdown string representing a header, beginning with '#' characters.
        """
        self.end_block()
        match = re.match(self.top_level_tags["h"], line)
        assert match is not None, "Header not found"

        level = len(match.group(1))
        content = match.group(2)

        self.dom.append(self.create_element(f"h{level}", children=[self.create_text(content)]))

    def handle_hr(self, line: 'str'):
        """Appends a horizontal rule to the DOM.
        
        Ends the current text block and inserts an <hr> element into the document model.
        """
        self.end_block()
        self.dom.append(self.create_element("hr", {}))

    def handle_text(self, line: 'str'):
        # Don't create text nodes for empty lines
        """
        Buffers a line of text for paragraph formation.
        
        If the line is empty or contains only whitespace, it delegates to the line break handler.
        Otherwise, it appends the line to an internal buffer to accumulate text for later
        conversion into a paragraph element.
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
        Parses a Markdown list from the provided text and appends it to the DOM.
        
        This function examines the text starting at the specified index to determine if it 
        represents an unordered or ordered list based on preset patterns. It aggregates list 
        items, supports nested lists by comparing indentation levels, and creates corresponding 
        list elements with their items. The constructed list is then added to the DOM, and the 
        function returns the number of lines processed.
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
        Parse a Markdown table starting at a given index.
        
        This method inspects the provided list of Markdown lines beginning at index i to
        determine if they form a valid table structure. A valid table requires at least a
        header row and a subsequent separator line. When detected, the method constructs
        a table element with separate header (<thead>) and body (<tbody>) sections, where
        cells in the header are rendered as <th> and those in the body as <td>. If the
        structure does not match a table, the line is processed as regular text.
        
        Args:
            text: A list of Markdown text lines.
            i: The starting index where table parsing should commence.
        
        Returns:
            The number of lines processed as part of the table.
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
        Processes a Markdown title line and updates the document head.
        
        Finalizes any ongoing text block, extracts the title from the provided line using a 
        predefined pattern, and creates a head element containing a title element with the 
        extracted text. An assertion error is raised if the line does not match the expected title format.
        """
        self.end_block()
        match = re.match(self.top_level_tags["title"], line)
        assert match is not None, "Title not found"

        title = match.group(1)
        self.head = self.create_element("head", children=[self.create_element("title", children=[self.create_text(title)])])

    def parse(self, markdown: 'str') -> 'ELEMENT':
        """
        Parses Markdown text into a structured HTML element.
        
        Splits the input Markdown text into lines and processes each one to identify
        block-level elements such as headers, blockquotes, code blocks, horizontal rules,
        lists, tables, and titles. It buffers regular text for paragraph creation and
        finalizes any pending content before assembling a DOM with head and body elements,
        which is then returned as an HTML element.
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