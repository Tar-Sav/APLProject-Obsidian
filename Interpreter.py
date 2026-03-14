from SymbolTable import SymbolTable
from Error import RuntimeErr


class Interpreter:
    def __init__(self):
        self.current_scope = SymbolTable()

    def interpret(self, node):
        try:
            result = self._visit(node)
            return result, None
        except RuntimeErr as e:
            return None, e

    # ── dispatch ──────────────────────────────────────────────────────────────

    def _visit(self, node):
        method = '_visit_' + type(node).__name__
        visitor = getattr(self, method, self._visit_generic)
        return visitor(node)

    def _visit_generic(self, node):
        raise RuntimeErr(f"Unknown AST node type: '{type(node).__name__}'")

    # ── structural nodes ──────────────────────────────────────────────────────

    def _visit_programNode(self, node):
        result = None
        for stmt in node.statements:
            result = self._visit(stmt)
        return result

    def _visit_blockNode(self, node):
        self.current_scope = self.current_scope.push_scope()
        result = None
        try:
            for stmt in node.statements:
                result = self._visit(stmt)
        finally:
            self.current_scope = self.current_scope.pop_scope()
        return result

    # ── literals ──────────────────────────────────────────────────────────────

    def _visit_numberNode(self, node):
        return node.value

    def _visit_stringNode(self, node):
        return node.value[1:-1]  # strip surrounding double-quotes the lexer leaves in

    def _visit_booleanNode(self, node):
        return node.value

    def _visit_charNode(self, node):
        return node.value

    # ── variables ─────────────────────────────────────────────────────────────

    def _visit_identifierNode(self, node):
        entry = self.current_scope.lookup(node.name)
        if entry is None:
            raise RuntimeErr(f"Variable '{node.name}' is not defined")
        value, _ = entry
        return value

    def _visit_varDeclNode(self, node):
        if node.value is not None:
            raw = self._visit(node.value)
            value = self._coerce(raw, node.dtype)
        else:
            value = self._default_value(node.dtype)
        self.current_scope.define(node.name, (value, node.dtype))
        return None  # declarations don't produce output

    def _visit_assignNode(self, node):
        raw = self._visit(node.value)
        entry = self.current_scope.lookup(node.name)
        if entry is None:
            raise RuntimeErr(f"Variable '{node.name}' is not defined")
        _, dtype = entry
        value = self._coerce(raw, dtype)
        self.current_scope.set(node.name, (value, dtype))
        return None  # assignments don't produce output

    # ── expressions ───────────────────────────────────────────────────────────

    def _visit_binaryOpNode(self, node):
        left  = self._visit(node.left)
        right = self._visit(node.right)
        op    = node.op

        def _numeric(a, b):
            if isinstance(a, bool) or isinstance(b, bool):
                raise RuntimeErr(f"Type mismatch: cannot apply '{op}' to bool")
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise RuntimeErr(
                    f"Type mismatch: cannot apply '{op}' to "
                    f"'{type(a).__name__}' and '{type(b).__name__}'"
                )

        try:
            if op == '+':
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                _numeric(left, right)
                return left + right
            if op == '-':
                _numeric(left, right)
                return left - right
            if op == '*':
                _numeric(left, right)
                return left * right
            if op == '/':
                _numeric(left, right)
                if right == 0:
                    raise RuntimeErr("Division by zero")
                return left / right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op in ('>', '>=', '<', '<='):
                _numeric(left, right)
                if op == '>':  return left > right
                if op == '>=': return left >= right
                if op == '<':  return left < right
                if op == '<=': return left <= right
        except RuntimeErr:
            raise
        except Exception as e:
            raise RuntimeErr(str(e))

    def _visit_unaryOpNode(self, node):
        val = self._visit(node.operand)
        if node.op == '-':
            if isinstance(val, bool):
                raise RuntimeErr("Unary minus not applicable to bool")
            if isinstance(val, (int, float)):
                return -val
            raise RuntimeErr(f"Unary minus not applicable to '{type(val).__name__}'")
        raise RuntimeErr(f"Unknown unary operator '{node.op}'")

    def _visit_ifNode(self, node):
        if self._visit(node.condition):
            return self._visit(node.then_block)
        elif node.else_block is not None:
            return self._visit(node.else_block)
        return None

    def _visit_whileNode(self, node):
        while self._visit(node.condition):
            self._visit(node.body)
        return None

    def _visit_forNode(self, node):
        # for-init lives in its own scope so the loop variable doesn't leak out
        self.current_scope = self.current_scope.push_scope()
        try:
            if node.init is not None:
                self._visit(node.init)
            while node.condition is None or self._visit(node.condition):
                self._visit(node.body)
                if node.update is not None:
                    self._visit(node.update)
        finally:
            self.current_scope = self.current_scope.pop_scope()
        return None

    def _visit_printNode(self, node):
        value = self._visit(node.value)
        print(value)
        return None  # already printed, don't let shell print it again

    # ── helpers ───────────────────────────────────────────────────────────────

    def _coerce(self, value, dtype):
        try:
            if dtype == 'int':
                if isinstance(value, bool):
                    raise RuntimeErr("Cannot convert bool to int")
                return int(value)
            if dtype == 'float':
                if isinstance(value, bool):
                    raise RuntimeErr("Cannot convert bool to float")
                return float(value)
            if dtype == 'bool':
                return bool(value)
            if dtype == 'char':
                s = str(value)
                if len(s) != 1:
                    raise RuntimeErr(f"char value must be a single character, got '{s}'")
                return s
            if dtype == 'string':
                return str(value)
        except RuntimeErr:
            raise
        except (ValueError, TypeError) as e:
            raise RuntimeErr(f"Cannot convert '{value}' to type '{dtype}': {e}")
        return value

    def _default_value(self, dtype):
        return {'int': 0, 'float': 0.0, 'bool': False, 'char': '\0', 'string': ''}.get(dtype)
