from SymbolTable import SymbolTable
from Error import SemanticError
import Obsidian_Parser as _P


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

    # ── type inference ────────────────────────────────────────────────────────

    def _type_of(self, node):
        if isinstance(node, _P.numberNode):
            return 'float' if isinstance(node.value, float) else 'int'
        if isinstance(node, _P.stringNode):
            return 'string'
        if isinstance(node, _P.booleanNode):
            return 'bool'
        if isinstance(node, _P.charNode):
            return 'char'
        if isinstance(node, _P.identifierNode):
            return self.current_scope.lookup(node.name)  # dtype string or None
        if isinstance(node, _P.binaryOpNode):
            if node.op in ('==', '!=', '>', '<', '>=', '<='):
                return 'bool'
            lt = self._type_of(node.left)
            rt = self._type_of(node.right)
            if 'float' in (lt, rt):
                return 'float'
            return lt
        if isinstance(node, _P.unaryOpNode):
            return self._type_of(node.operand)
        return None  # can't determine

    def _compatible(self, declared, expr_type):
        if expr_type is None:
            return True  # unknown — skip check
        if declared == expr_type:
            return True
        if declared == 'float' and expr_type == 'int':
            return True  # int literal is fine for float var
        return False

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
            expr_type = self._type_of(node.value)
            if not self._compatible(node.dtype, expr_type):
                self._error(
                    f"Type mismatch: cannot assign '{expr_type}' to '{node.dtype}' variable '{node.name}'"
                )

    def _visit_assignNode(self, node):
        declared = self.current_scope.lookup(node.name)
        if declared is None:
            self._error(f"Variable '{node.name}' used before declaration")
        self._visit(node.value)
        if declared is not None:
            expr_type = self._type_of(node.value)
            if not self._compatible(declared, expr_type):
                self._error(
                    f"Type mismatch: cannot assign '{expr_type}' to '{declared}' variable '{node.name}'"
                )

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
