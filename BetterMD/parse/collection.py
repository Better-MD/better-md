import typing as t
import logging
from ..html import CustomHTML

if t.TYPE_CHECKING:
    from ..elements import Symbol

class Collection:
    def __init__(self, *symbols:'type[Symbol]'):
        """
        Initializes a Collection instance with optional Symbol objects.
        
        Stores the provided symbols in a list and sets up a logger for diagnostic purposes.
        
        Args:
            *symbols: One or more Symbol instances to include in the collection.
        """
        self.symbols = list(symbols)
        self.logger = logging.getLogger("BetterMD")

    def add_symbols(self, symbol:'type[Symbol]'):
        """
        Appends a symbol to the collection.
        
        Args:
            symbol: A Symbol instance to add to the collection.
        """
        self.symbols.append(symbol)

    def remove_symbol(self, symbol:'type[Symbol]'):
        """
        Remove a symbol from the collection.
        
        Removes the specified symbol from the internal list of symbols. If the symbol is not present, a ValueError is raised.
        """
        self.symbols.remove(symbol)

    def find_symbol(self, name:'str', raise_errors:'bool'=False) -> 't.Union[None, type[Symbol]]':
        """
        Searches for a symbol with a matching HTML representation.
        
        Iterates over the collection's symbols and returns the first symbol whose HTML is
        either a string that exactly matches the given name or, if a CustomHTML instance,
        successfully verifies the name. If no match is found and raise_errors is True, a
        ValueError is raised; otherwise, None is returned.
        
        Args:
            name: The symbol name to match against the HTML representation.
            raise_errors: If True, raises an error when no matching symbol is found.
        
        Returns:
            The matching symbol if found, or None if not found and raise_errors is False.
        
        Raises:
            ValueError: If no matching symbol is found and raise_errors is set to True.
        """
        for symbol in self.symbols:
            if isinstance(symbol.html, str) and symbol.html == name:
                return symbol
            elif isinstance(symbol.html, CustomHTML) and symbol.html.verify(name):
                return symbol

        if raise_errors:
            raise ValueError(f"Symbol `{name}` not found in collection, if using default symbols it may not be supported.")
        return None