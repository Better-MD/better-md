from .typing import ELEMENT
import typing as t

class HTMLParser:
    def __init__(self):
        """
        Initialize an HTMLParser instance.
        
        Resets the parser's internal state to prepare for parsing operations.
        """
        self.reset()

    def reset(self):
        """
        Resets the parser state to its initial configuration.
        
        Clears the DOM, current tag, text buffer, attribute name, and tag stack, and resets the state to process text.
        """
        self.current_tag:'t.Optional[ELEMENT]' = None
        self.dom = []
        self.state = 'TEXT'
        self.buffer = ''
        self.attr_name = ''
        self.tag_stack = []

    def parse(self, html:'str') -> 'list[ELEMENT]':
        """
        Parse an HTML string and construct a DOM representation.
        
        Resets the parser's internal state and processes the input HTML one character at a time,
        transitioning between states to support text nodes, opening tags, self-closing tags,
        closing tags, and attributes. The method builds a nested DOM structure from the HTML
        and returns it as a list of elements.
        
        Args:
            html: The HTML string to parse.
        
        Returns:
            list[ELEMENT]: A list representing the parsed DOM elements.
        """
        self.reset()

        i = 0
        while i < len(html):
            char = html[i]

            if self.state == 'TEXT':
                if char == '<':
                    if self.buffer.strip():
                        self.handle_text(self.buffer)
                    self.buffer = ''
                    self.state = 'TAG_START'
                else:
                    self.buffer += char

            elif self.state == 'TAG_START':
                if char == '/':
                    self.state = 'CLOSING_TAG'
                elif char == '!':
                    self.state = 'COMMENT_OR_DOCTYPE'
                    self.buffer = '!'
                else:
                    self.state = 'TAG_NAME'
                    self.buffer = char

            elif self.state == 'TAG_NAME':
                if char.isspace():
                    self.current_tag = {"type": "element", 'name': self.buffer, 'attributes': {}, 'children': []}
                    self.buffer = ''
                    self.state = 'BEFORE_ATTRIBUTE_NAME'
                elif char == '>':
                    self.current_tag = {"type": "element", 'name': self.buffer, 'attributes': {}, 'children': []}
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                elif char == '/':
                    self.current_tag = {"type": "element", 'name': self.buffer, 'attributes': {}, 'children': []}
                    self.state = 'SELF_CLOSING_TAG'
                else:
                    self.buffer += char

            elif self.state == 'BEFORE_ATTRIBUTE_NAME':
                if char.isspace():
                    pass
                elif char == '>':
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                elif char == '/':
                    self.state = 'SELF_CLOSING_TAG'
                else:
                    self.attr_name = char
                    self.state = 'ATTRIBUTE_NAME'

            elif self.state == 'ATTRIBUTE_NAME':
                if char.isspace():
                    self.current_tag['attributes'][self.attr_name] = ''
                    self.state = 'AFTER_ATTRIBUTE_NAME'
                elif char == '=':
                    self.state = 'BEFORE_ATTRIBUTE_VALUE'
                elif char == '>':
                    self.current_tag['attributes'][self.attr_name] = ''
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                elif char == '/':
                    self.current_tag['attributes'][self.attr_name] = ''
                    self.state = 'SELF_CLOSING_TAG'
                else:
                    self.attr_name += char

            elif self.state == 'AFTER_ATTRIBUTE_NAME':
                if char.isspace():
                    pass
                elif char == '=':
                    self.state = 'BEFORE_ATTRIBUTE_VALUE'
                elif char == '>':
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                elif char == '/':
                    self.state = 'SELF_CLOSING_TAG'
                else:
                    self.current_tag['attributes'][self.attr_name] = ''
                    self.attr_name = char
                    self.state = 'ATTRIBUTE_NAME'

            elif self.state == 'BEFORE_ATTRIBUTE_VALUE':
                if char.isspace():
                    pass
                elif char == '"':
                    self.buffer = ''
                    self.state = 'ATTRIBUTE_VALUE_DOUBLE_QUOTED'
                elif char == "'":
                    self.buffer = ''
                    self.state = 'ATTRIBUTE_VALUE_SINGLE_QUOTED'
                elif char == '>':
                    self.current_tag['attributes'][self.attr_name] = ''
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                else:
                    self.buffer = char
                    self.state = 'ATTRIBUTE_VALUE_UNQUOTED'

            elif self.state == 'ATTRIBUTE_VALUE_DOUBLE_QUOTED':
                if char == '"':
                    self.current_tag['attributes'][self.attr_name] = self.buffer
                    self.buffer = ''
                    self.state = 'AFTER_ATTRIBUTE_VALUE_QUOTED'
                else:
                    self.buffer += char

            elif self.state == 'ATTRIBUTE_VALUE_SINGLE_QUOTED':
                if char == "'":
                    self.current_tag['attributes'][self.attr_name] = self.buffer
                    self.buffer = ''
                    self.state = 'AFTER_ATTRIBUTE_VALUE_QUOTED'
                else:
                    self.buffer += char

            elif self.state == 'ATTRIBUTE_VALUE_UNQUOTED':
                if char.isspace():
                    self.current_tag['attributes'][self.attr_name] = self.buffer
                    self.buffer = ''
                    self.state = 'BEFORE_ATTRIBUTE_NAME'
                elif char == '>':
                    self.current_tag['attributes'][self.attr_name] = self.buffer
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                elif char == '/':
                    self.current_tag['attributes'][self.attr_name] = self.buffer
                    self.buffer = ''
                    self.state = 'SELF_CLOSING_TAG'
                else:
                    self.buffer += char

            elif self.state == 'AFTER_ATTRIBUTE_VALUE_QUOTED':
                if char.isspace():
                    self.state = 'BEFORE_ATTRIBUTE_NAME'
                elif char == '/':
                    self.state = 'SELF_CLOSING_TAG'
                elif char == '>':
                    self.handle_tag_open(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                else:
                    self.state = 'BEFORE_ATTRIBUTE_NAME'
                    i -= 1  # Reconsider this character

            elif self.state == 'SELF_CLOSING_TAG':
                if char == '>':
                    self.handle_tag_self_closing(self.current_tag)
                    self.buffer = ''
                    self.state = 'TEXT'
                else:
                    # Error handling
                    pass

            elif self.state == 'CLOSING_TAG':
                if char == '>':
                    self.handle_tag_close(self.buffer)
                    self.buffer = ''
                    self.state = 'TEXT'
                else:
                    self.buffer += char

            # Additional states would be implemented here

            i += 1

        # Handle any remaining text
        if self.state == 'TEXT' and self.buffer.strip():
            self.handle_text(self.buffer)
            
        return self.dom

    def handle_tag_open(self, tag):
        """
        Adds an open tag to the DOM and updates the tag stack.
        
        If a tag is already open, appends the new tag as a child of the current tag; otherwise, it is added
        to the root of the DOM. The new tag is then pushed onto the tag stack.
        """
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(tag)
        else:
            self.dom.append(tag)

        self.tag_stack.append(tag)

    def handle_tag_self_closing(self, tag):
        """
        Adds a self-closing tag node to the DOM.
        
        If an open tag exists in the tag stack, appends the self-closing tag as a child of the most recent tag; otherwise, adds it to the root DOM.
        """
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(tag)
        else:
            self.dom.append(tag)

    def handle_tag_close(self, tag_name):
        """
        Closes the open tag if its name matches the provided tag name.
        
        If the last element in the tag stack has a name equal to tag_name, the tag is removed,
        effectively closing the tag in the DOM structure.
        """
        if len(self.tag_stack) > 0 and self.tag_stack[-1]['name'] == tag_name:
            self.tag_stack.pop()

    def handle_text(self, text):
        """
        Adds a text node to the appropriate parent in the DOM.
        
        If there is an open tag on the stack, the text node is appended as a child of that tag;
        otherwise, it is added to the top-level DOM list.
        """
        text_node = {'type': 'text', 'content': text, 'name': 'text'}
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(text_node)
        else:
            self.dom.append(text_node)

    def get_dom(self):
        """
        Retrieves the constructed DOM representation.
        
        Returns:
            list: A list representing the parsed Document Object Model.
        """
        return self.dom