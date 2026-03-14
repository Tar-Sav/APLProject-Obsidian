from SymbolTable import SymbolTable
from Error import SemanticError


class SemanticAnalyzer:
    def __init__(self):
        self.current_scope = SymbolTable()

    def analyze(self, node):
        """Walk the AST and return a list of SemanticErrors (empty = no errors)."""
        self.errors = []
        self._visit(node)
        return self.errors

    def _error(self, msg):
        self.errors.append(SemanticError(msg))

    def _visit(self, node):
        method = '_visit_' + type(node).__name__
        visitor = getattr(self, method, self._visit_generic)
        return visitor(node)

    def _visit_generic(self, node):
        pass

    # ── structural ────────────────────────────────────────────────────────────

    def _visit_programNode(self, node):
        for stmt in node.statements:
            self._visit(stmt)

    def _visit_blockNode(self, node):
        self.current_scope = self.current_scope.push_scope()
        try:
            for stmt in node.statements:
                self._visit(stmt)
        finally:
            self.current_scope = self.current_scope.pop_scope()

    # ── statements ────────────────────────────────────────────────────────────

    def _visit_varDeclNode(self, node):
        if self.current_scope.is_defined_locally(node.name):
            self._error(f"Variable '{node.name}' already declared in this scope")
        else:
            self.current_scope.define(node.name, node.dtype)
        if node.value is not None:
            self._visit(node.value)

    def _visit_assignNode(self, node):
        if self.current_scope.lookup(node.name) is None:
            self._error(f"Variable '{node.name}' used before declaration")
        self._visit(node.value)

    def _visit_ifNode(self, node):
        self._visit(node.condition)
        self._visit(node.then_block)
        if node.else_block is not None:
            self._visit(node.else_block)

    def _visit_whileNode(self, node):
        self._visit(node.condition)
        self._visit(node.body)

    def _visit_forNode(self, node):
        # for-loop init declares into its own scope so the var is not visible outside
        self.current_scope = self.current_scope.push_scope()
        try:
            if node.init is not None:
                self._visit(node.init)
            if node.condition is not None:
                self._visit(node.condition)
            if node.update is not None:
                self._visit(node.update)
            self._visit(node.body)
        finally:
            self.current_scope = self.current_scope.pop_scope()

    def _visit_printNode(self, node):
        self._visit(node.value)

    # ── expressions ───────────────────────────────────────────────────────────

    def _visit_identifierNode(self, node):
        if self.current_scope.lookup(node.name) is None:
            self._error(f"Variable '{node.name}' used before declaration")

    def _visit_binaryOpNode(self, node):
        self._visit(node.left)
        self._visit(node.right)

    def _visit_unaryOpNode(self, node):
        self._visit(node.operand)

    # ── literals (no checks needed) ───────────────────────────────────────────

    def _visit_numberNode(self, node):  pass
    def _visit_stringNode(self, node):  pass
    def _visit_booleanNode(self, node): pass
    def _visit_charNode(self, node):    pass
