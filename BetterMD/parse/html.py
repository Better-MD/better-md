from .typing import ELEMENT
import typing as t

class HTMLParser:
    def __init__(self):
        """
        Initialize an HTMLParser instance.
        
        Resets the parser's internal state to prepare for HTML parsing.
        """
        self.reset()

    def reset(self):
        """
        Resets the parser to its initial state.
        
        Clears all stored parsing data including the current tag, DOM, internal state, buffer,
        attribute name, and tag stack to prepare for new HTML input.
        """
        self.current_tag:'t.Optional[ELEMENT]' = None
        self.dom = []
        self.state = 'TEXT'
        self.buffer = ''
        self.attr_name = ''
        self.tag_stack = []

    def parse(self, html:'str') -> 'list[ELEMENT]':
        """
        Parses an HTML string into a Document Object Model (DOM).
        
        This method resets the parser's state and processes the input one character at a time using
        a state machine, handling text nodes, opening tags, attributes, self-closing tags, and closing
        tags. Any remaining text is appended as a text node, and the complete DOM is returned as a list
        of elements.
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
        Handles an opening tag by incorporating it into the DOM and updating the tag stack.
        
        If there is an active tag, the new tag is added as its child; otherwise, it is added 
        as a top-level element. The tag is then pushed onto the tag stack to track nested elements.
        """
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(tag)
        else:
            self.dom.append(tag)

        self.tag_stack.append(tag)

    def handle_tag_self_closing(self, tag):
        """
        Handles a self-closing HTML tag by appending it to the appropriate parent in the DOM.
        
        If there is an open tag (i.e., the tag stack is not empty), the tag is added as a child of
        the most recent tag on the stack. Otherwise, it is appended directly to the DOM.
        """
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(tag)
        else:
            self.dom.append(tag)

    def handle_tag_close(self, tag_name):
        """
        Closes the last opened tag if its name matches the provided tag name.
        
        If the tag stack is not empty and the top tag's name equals tag_name, it is removed
        from the stack to correctly update the open tags during parsing.
        """
        if len(self.tag_stack) > 0 and self.tag_stack[-1]['name'] == tag_name:
            self.tag_stack.pop()

    def handle_text(self, text):
        """
        Adds a text node to the DOM.
        
        Constructs a text node as a dictionary with keys 'type', 'content', and 'name' set to "text" and the provided text. The node is appended to the children of the most recently opened tag if one exists; otherwise, it is added to the DOM root.
        """
        text_node = {'type': 'text', 'content': text, 'name': 'text'}
        if len(self.tag_stack) > 0:
            self.tag_stack[-1]['children'].append(text_node)
        else:
            self.dom.append(text_node)

    def get_dom(self):
        """
        Returns the constructed Document Object Model.
        
        This method provides access to the DOM built from the parsed HTML content.
        """
        return self.dom