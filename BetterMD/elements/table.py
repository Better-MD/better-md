from .symbol import Symbol
from ..markdown import CustomMarkdown
from ..rst import CustomRst
from .h import H1, H2, H3, H4, H5, H6
from .text import Text
import itertools as it

class TableMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Generate Markdown for a table element.
        
        Iterates over the provided inner elements to construct the table's Markdown output.
        Processes a THead element to generate the header and collects non-empty Markdown
        from each TBody element as table rows. The header and rows are concatenated with
        newline separators to form the final Markdown string.
        
        Returns:
            str: The complete Markdown representation of the table.
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
        Converts table sections into a reStructuredText formatted table.
        
        This method processes a list of table sections (typically header and body) to generate an RST table. It first
        iterates over the sections to compute the maximum width for each column by examining each cell’s content. In a
        second pass, it builds a table string with consistent column widths, using a distinct separator (with '=' characters)
        after header rows and '-' characters for body rows. If no valid rows are found, an empty string is returned.
        
        Args:
            inner: A list of table section symbols (e.g., THead and TBody) that contain the table rows.
        
        Returns:
            str: The formatted reStructuredText table.
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
        Convert table rows to a Markdown formatted table.
        
        Iterates over each row in the input, converting its cells to Markdown and
        computing the maximum width for each column. The function then constructs
        a pipe-delimited table string and appends a separator row composed of dashes.
        Returns an empty string if no rows are provided.
        
        Args:
            inner: Iterable of row elements, each having a 'children' attribute
                   with cell elements that implement a to_md() method.
            symbol: Ignored; provided for interface compatibility.
            parent: Ignored; provided for interface compatibility.
        
        Returns:
            A Markdown formatted string representing the table.
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
        Return an empty string as RST conversion is handled by TableRST.
        
        This placeholder method satisfies the interface requirement without performing any
        direct header conversion, as all RST formatting for headers is managed by the TableRST class.
        """
        return ""

class TBodyMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Generate a Markdown string by converting each inner row.
        
        This method iterates over the provided inner elements and converts each row to its
        Markdown representation using the row's to_md() method. The resulting Markdown
        string is generated by joining the individual row outputs with newline characters.
        If no inner elements are provided, an empty string is returned.
        
        Args:
            inner: A collection of row elements, each supporting a to_md() conversion.
            symbol: An element symbol (unused) for interface consistency.
            parent: The parent element (unused) for context.
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
        Converts inner cells to a Markdown table row.
        
        Iterates over each element in the provided list, converting it to Markdown and
        joining the results with pipe characters. The returned string is enclosed
        with leading and trailing pipes.
        """
        cells = [cell.to_md() for cell in inner]
        return f"|{'|'.join(cells)}|"

class TrRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Placeholder for table header RST conversion.
        
        This method returns an empty string as RST conversion for table headers is handled by TableRST.
        """
        return ""

class TdMD(CustomMarkdown):
    def to_md(self, inner, symbol, parent):
        """
        Converts inner elements to a Markdown string.
        
        Processes each element in the provided iterable by calling its to_md() method and
        joins the resulting strings using a space separator.
        
        Returns:
            str: The concatenated Markdown representation.
        """
        return " ".join([e.to_md() for e in inner])

class TdRST(CustomRst):
    def to_rst(self, inner: list[Symbol], symbol: Symbol, parent: Symbol) -> str:
        """Convert inner content to its reStructuredText representation.
        
        Returns an empty string if no inner content is provided. If there is exactly one
        symbol and it is of a text or heading type (Text, H1, H2, H3, H4, H5, H6), its
        reStructuredText output is returned directly. Otherwise, the method concatenates
        the reStructuredText outputs of all inner symbols with a space.
        """
        if not inner:
            return ""
            
        if len(inner) > 1 or not isinstance(inner[0], (Text, H1, H2, H3, H4, H5, H6)):
            return " ".join([e.to_rst() for e in inner])  # Fallback to join instead of raising error
        return inner[0].to_rst()

class ThRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        """
        Generates a reStructuredText string from inner elements.
        
        Iterates over each element in the provided list, calling its `to_rst()` method
        and joining the results with spaces. The `symbol` and `parent` parameters are
        present for interface consistency and are not used.
        """
        return " ".join([e.to_rst() for e in inner])

class TBodyRST(CustomRst):
    def to_rst(self, inner, symbol, parent):
        # This is now handled by TableRST
        """
        Placeholder method for generating reStructuredText for a table header.
        
        This method returns an empty string because header processing is handled by TableRST.
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