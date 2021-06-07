############################################
# CONTEXT
############################################


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


############################################
# SYMBOL TABLE
############################################


class SymbolTable:
    """
    Stores all variables that have been assigned
    """

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.symbols}"

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
