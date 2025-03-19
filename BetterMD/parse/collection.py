import typing as t
import logging
from ..html import CustomHTML

if t.TYPE_CHECKING:
    from ..elements import Symbol

class Collection:
    def __init__(self, *symbols:'type[Symbol]'):
        """
        Initialize a Collection instance with optional symbols.
        
        Args:
            *symbols: Initial Symbol instances to include in the collection.
        
        The logger is configured using the "BetterMD" namespace.
        """
        self.symbols = list(symbols)
        self.logger = logging.getLogger("BetterMD")

    def add_symbols(self, symbol:'type[Symbol]'):
        """
        Appends a symbol to the collection.
        
        The provided symbol is added to the internal list of symbols.
        """
        self.symbols.append(symbol)

    def remove_symbol(self, symbol:'type[Symbol]'):
        """
        Removes the specified symbol from the collection.
        
        Args:
            symbol: The Symbol instance to remove.
        """
        self.symbols.remove(symbol)

    def find_symbol(self, name:'str', raise_errors:'bool'=False) -> 't.Union[None, type[Symbol]]':
        """
        Finds a symbol in the collection by matching its HTML attribute.
        
        Iterates over the collection's symbols and returns the first symbol for which the `html`
        attribute matches the provided name either directly (if it is a string) or via the
        `verify` method (if it is an instance of CustomHTML). If no matching symbol is found,
        the function returns None unless raise_errors is True, in which case it raises a ValueError.
        
        Args:
            name: The name to search for in the symbol's HTML representation.
            raise_errors: If True, raises a ValueError when no matching symbol is found.
        
        Returns:
            The matching symbol if found; otherwise, None.
        
        Raises:
            ValueError: If no symbol is found and raise_errors is True.
        """
        for symbol in self.symbols:
            if isinstance(symbol.html, str) and symbol.html == name:
                return symbol
            elif isinstance(symbol.html, CustomHTML) and symbol.html.verify(name):
                return symbol

        if raise_errors:
            raise ValueError(f"Symbol `{name}` not found in collection, if using default symbols it may not be supported.")
        return None