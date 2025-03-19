from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .h import H1, H2, H3, H4, H5, H6
from .text import Text
import itertools as it

class TableMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Convert table sections to a Markdown formatted string.
        
        Iterates over the provided table sections, converting header sections (THead) and body
        sections (TBody) using their respective to_md methods. The header is extracted from the
        first encountered THead element, and all non-empty TBody outputs are combined with line
        breaks to form the final Markdown table.
        """
        result = []
        thead_content = ""
        tbody_rows = []
        
        # Process inner elements
        for section in inner:
            if isinstance(section, THead):
                thead_content = section.to_md()
            elif isinstance(section, TBody):
                tbody_content = section.to_md()
                if tbody_content:
                    tbody_rows.append(tbody_content)
        
        # Combine all parts
        if thead_content:
            result.append(thead_content)
        
        if tbody_rows:
            result.append("\n".join(tbody_rows))
        
        return "\n".join(result)
   
class TableRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Convert table sections to a reStructuredText formatted table.
        
        Iterates over provided table header (THead) and body (TBody) sections to compute
        the maximum column widths based on cell content. Constructs a table with a top
        border, formatted rows with left-aligned cells, and row separators (using "="
        for header rows and "-" for others). Returns an empty string if no valid sections
        or rows are found.
        """
        if not inner:
            return ""
        
        # First pass: collect all cell widths from both thead and tbody
        col_widths = []
        all_rows = []
        
        for section in inner:
            if isinstance(section, THead) or isinstance(section, TBody):
                for row in section.children:
                    cells = [cell.to_rst() for cell in row.children]
                    all_rows.append((cells, isinstance(section, THead)))
                    
                    # Update column widths
                    if not col_widths:
                        col_widths = [len(cell) for cell in cells]
                    else:
                        col_widths = [max(old, len(new)) for old, new in zip(col_widths, cells + [''] * (len(col_widths) - len(cells)))]
        
        if not all_rows:
            return ""
        
        # Second pass: generate RST with consistent widths
        result = []
        
        # Top border
        top_border = "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"
        result.append(top_border)
        
        for i, (cells, is_header) in enumerate(all_rows):
            # Create row with proper spacing using consistent column widths
            row = "| " + " | ".join(cell.ljust(width) for cell, width in zip(cells, col_widths)) + " |"
            result.append(row)
            
            # Add separator after each row
            if is_header:
                separator = "+" + "+".join(["=" * (width + 2) for width in col_widths]) + "+"
            else:
                separator = "+" + "+".join(["-" * (width + 2) for width in col_widths]) + "+"
            result.append(separator)
        
        return "\n".join(result)

class THeadMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Generate Markdown table rows with aligned columns.
        
        Iterates over each row in the input by converting its cell elements to Markdown,
        calculates the maximum width for each column, and constructs the table rows using
        pipe delimiters. A separator row of dashes matching each column's width is appended.
        Returns an empty string if the input list is empty.
        
        Args:
            inner: A list of row elements, each having a 'children' attribute with cell items.
        
        Returns:
            A string containing the formatted Markdown table.
        """
        if not inner:
            return ""
            
        rows = []
        widths = []
        
        # First pass: collect all rows and calculate column widths
        for row in inner:
            row_cells = [cell.to_md() for cell in row.children]
            if not widths:
                widths = [len(cell) for cell in row_cells]
            else:
                widths = [max(old, len(new)) for old, new in zip(widths, row_cells)]
            rows.append(row_cells)
        
        if not rows:
            return ""
        
        # Second pass: generate properly formatted markdown
        result = []
        for row_cells in rows:
            row = "|" + "|".join(row_cells) + "|"
            result.append(row)
        
        # Add separator row
        separator = "|" + "|".join(["-" * width for width in widths]) + "|"
        result.append(separator)
        
        return "\n".join(result)

class THeadRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """Return an empty string.
        
        The conversion of the table body to reStructuredText is handled by the TableRST class.
        """
        return ""

class TBodyMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts a list of row elements to a Markdown string.
        
        Iterates over each element in the provided list by calling its `to_md()`
        method and joins the resulting Markdown rows with newline characters.
        Returns an empty string if the list is empty.
        """
        if not inner:
            return ""
        
        rows = []
        for row in inner:
            rows.append(row.to_md())
        
        return "\n".join(rows)

class TrMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts a list of cell objects into a Markdown-formatted table row.
        
        Each cell is processed using its `to_md` method and the resulting strings are
        joined using the pipe character (|) as a delimiter, with a leading and trailing
        pipe added to conform to Markdown table row syntax.
        
        Args:
            inner: List of cell objects to convert.
            
        Returns:
            A string representing the Markdown-formatted table row.
        """
        cells = [cell.to_md() for cell in inner]
        return f"|{'|'.join(cells)}|"

class TrRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Delegates header conversion to TableRST.
        
        This method returns an empty string because header processing is handled by
        the TableRST class.
        """
        return ""

class TdMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts a list of elements to a Markdown string.
        
        Iterates over each element in the provided list, calls its to_md method, and
        joins the resulting strings with a space.
        
        Args:
            inner: A list of elements supporting a to_md conversion.
            symbol: The current symbol context (unused).
            parent: The parent symbol context (unused).
        
        Returns:
            A string containing the Markdown representations of the inner elements.
        """
        return " ".join([e.to_md() for e in inner])

class TdRST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol) -> str:
        """
        Converts inner symbols to their reStructuredText representation.
        
        Returns an empty string if no inner symbols are provided. If a single element of type Text or a heading (H1–H6)
        is present, its reStructuredText conversion is returned. Otherwise, the reStructuredText representations of all
        inner symbols are joined together with spaces as a fallback.
        """
        if not inner:
            return ""
            
        if len(inner) > 1 or not isinstance(inner[0], (Text, H1, H2, H3, H4, H5, H6)):
            return " ".join([e.to_rst() for e in inner])  # Fallback to join instead of raising error
        return inner[0].to_rst()

class ThRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Convert inner elements to their reStructuredText (RST) representations.
        
        Iterates over each element in the provided list, converts it to its RST format, and
        joins the results with a space. The 'symbol' and 'parent' parameters are included for
        interface consistency.
        
        Returns:
            A string containing the RST representations of the inner elements.
        """
        return " ".join([e.to_rst() for e in inner])

class TBodyRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Returns an empty string.
        
        This method acts as a placeholder for table body conversion to reStructuredText,
        since the complete formatting is handled by the TableRST class.
        """
        return ""

class Table(Symbol):
    html = "table"
    md = TableMD()
    rst = TableRST()
    nl = True

class Tr(Symbol):
    html = "tr"
    md = TrMD()
    rst = TrRST()

class Td(Symbol):
    html = "td"
    md = TdMD()
    rst = TdRST()

class Th(Symbol):
    html = "th"
    md = TdMD()
    rst = ThRST()

class THead(Symbol):
    html = "thead"
    md = THeadMD()
    rst = THeadRST()

class TBody(Symbol):
    html = "tbody"
    md = TBodyMD()
    rst = TBodyRST()