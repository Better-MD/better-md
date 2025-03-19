from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .h import H1, H2, H3, H4, H5, H6
from .text import Text
import itertools as it

class TableMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Generate a Markdown representation of a table.
        
        Processes provided elements by converting header (THead) and body (TBody) sections into
        their Markdown representations and concatenates them with appropriate line breaks.
        If a header is present, it is rendered first, followed by any body rows.
        
        Returns:
            str: The combined Markdown formatted string representing the table.
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
        Generates a reStructuredText representation of a table.
        
        This method processes a sequence of table sections (headers and bodies) to compute
        consistent column widths and generate a formatted table with borders and row separators.
        It iterates over header and body sections to determine the spacing for each column and
        then renders the final table. Returns an empty string if no valid table rows are found.
        
        Args:
            inner: A list of table section symbols (THead or TBody) containing table rows.
            symbol: The current table symbol (not used in the RST formatting).
            parent: The parent symbol of the current table element (not used in the RST formatting).
        
        Returns:
            A string representing the table in reStructuredText format.
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
        Generate markdown for table header rows and a separator.
        
        This method iterates over the provided row elements, converting each child cell
        to its markdown representation while determining the maximum column widths for
        consistent formatting. It then constructs each row with pipe delimiters and appends
        a final separator row composed of dashes. Returns an empty string if no rows are provided.
        
        Args:
            inner: A collection of row elements, each containing cells to be formatted.
            symbol: Unused parameter representing the current symbol.
            parent: Unused parameter representing the parent element.
        
        Returns:
            A markdown formatted string representing the table header rows followed by a separator,
            or an empty string if there are no rows.
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
        """
        Placeholder for RST conversion.
        
        This method does not perform any conversion and simply returns an empty string,
        as reStructuredText rendering is delegated to the TableRST class.
        """
        return ""

class TBodyMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts a list of row elements to Markdown.
        
        Iterates over each element in the provided inner list, calling its to_md method,
        and joins the resulting strings with newline characters. Returns an empty string
        if no inner elements are provided.
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
        Converts a list of cell elements into a Markdown table row.
        
        Iterates over each cell in `inner`, calling its `to_md()` method, and joins the resulting
        strings with pipe characters. A leading and trailing pipe are added to complete the row format.
        
        Args:
            inner: A list of cell objects where each object provides a Markdown representation.
            symbol: Represents the current row's symbol (provided for interface consistency; unused).
            parent: The parent element in the document structure (provided for interface consistency; unused).
        
        Returns:
            A string formatted as a Markdown table row.
        """
        cells = [cell.to_md() for cell in inner]
        return f"|{'|'.join(cells)}|"

class TrRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Return an empty string because RST conversion is handled by TableRST.
        
        This placeholder method exists solely to fulfill the interface and does not perform any conversion.
        """
        return ""

class TdMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Convert inner elements to a Markdown string.
        
        Processes each element in the provided inner list by invoking its to_md method
        and joining the resulting strings with a space. The symbol and parent parameters
        are included to comply with the interface but are not used in the conversion.
        
        Returns:
            str: The concatenated Markdown output of all inner elements.
        """
        return " ".join([e.to_md() for e in inner])

class TdRST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol) -> str:
        """
        Generate an RST representation for cell content.
        
        Converts a list of inner symbols into an RST-formatted string. Returns an empty
        string if no symbols are provided. When more than one symbol is present or when the
        single symbol is not a standard text or header type, their RST outputs are joined
        with spaces as a fallback mechanism. Otherwise, returns the RST output of the single
        symbol.
        
        Note:
            The parameters 'symbol' and 'parent' are included for interface consistency.
        """
        if not inner:
            return ""
            
        if len(inner) > 1 or not isinstance(inner[0], (Text, H1, H2, H3, H4, H5, H6)):
            return " ".join([e.to_rst() for e in inner])  # Fallback to join instead of raising error
        return inner[0].to_rst()

class ThRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Renders a collection of elements as a reStructuredText string.
        
        Iterates over each element in the provided inner list, calling its to_rst() method,
        and concatenates the results with a space as the separator.
        """
        return " ".join([e.to_rst() for e in inner])

class TBodyRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Return an empty reStructuredText string.
        
        This placeholder method returns an empty string because the conversion of
        these elements is delegated to the TableRST class.
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