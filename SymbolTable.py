class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self._symbols = {}

    def push_scope(self):
        return SymbolTable(parent=self)

    def pop_scope(self):
        if self.parent is None:
            raise Exception("Cannot pop the global scope")
        return self.parent

    def define(self, name, value):
        self._symbols[name] = value

    def lookup(self, name):
        if name in self._symbols:
            return self._symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def set(self, name, value):
        if name in self._symbols:
            self._symbols[name] = value
            return True
        if self.parent:
            return self.parent.set(name, value)
        return False

    def is_defined_locally(self, name):
        return name in self._symbols
