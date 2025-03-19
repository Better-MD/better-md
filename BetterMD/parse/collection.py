import typing as t
import logging
from ..html import CustomHTML

if t.TYPE_CHECKING:
    from ..elements import Symbol

class Collection:
    def __init__(self, *symbols:'type[Symbol]'):
        """
        Initializes a Collection instance with the provided symbols.
        
        Args:
            *symbols: Variable number of Symbol instances to populate the collection.
        
        Also configures a logger named "BetterMD".
        """
        self.symbols = list(symbols)
        self.logger = logging.getLogger("BetterMD")

    def add_symbols(self, symbol:'type[Symbol]'):
        """
        Adds a Symbol to the collection.
        
        Appends the provided Symbol instance to the collection's internal list of symbols.
        """
        self.symbols.append(symbol)

    def remove_symbol(self, symbol:'type[Symbol]'):
        """
        Removes the specified symbol from the collection.
        
        If the symbol is not present in the collection, a ValueError is raised.
        """
        self.symbols.remove(symbol)

    def find_symbol(self, name:'str', raise_errors:'bool'=False) -> 't.Union[None, type[Symbol]]':
        """
        Searches for a symbol matching the given name in the collection.
        
        This method iterates over the collection's symbols. It returns the first symbol whose `html`
        attribute is either a string equal to the provided name or an instance of CustomHTML that verifies
        a match via its `verify` method. If no matching symbol is found, a ValueError is raised when
        raise_errors is True; otherwise, the method returns None.
        
        Parameters:
            name: The name to match against a symbol's html attribute.
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