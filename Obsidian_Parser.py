import ply.yacc as yacc
from Obsidian_Lexer import tokens
from Error import Error

class numberNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'Number({self.value})'
    
class identifierNode:
    def __init__(self, name):
        self.name = name
    def __repr__ (self):
        return f'Identifier({self.name})'

class stringNode:
    def __init__(self,value):
        self.value = value
    def __repr__(self):
        return f'String ("{self.value}")'

class charNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Char('{self.value}')"

class booleanNode:
    def __init__(self,value):
        self.value = value
    def __repr__ (self):
        return f'Boolean({self.value})'

#This stores the operation between two things. Example x + 5
#It needs a left, the operator (what's in the middle?) and a right side
class binaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f'BinOp({self.left}{self.op}{self.right})'

#Stores operations on one thing like -x that obviously need one operand
class unaryOpNode:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def __repr__(self):
        return f'UnaryOp({self.op}{self.operand})'

class varDeclNode:
    def __init__(self, dtype, name, value=None):
        self.dtype = dtype
        self.name = name
        self.value = value
    def __repr__(self):
        return f'VarDecl({self.dtype}{self.name} = {self.value})'

#This is different from varDeclNode. this allows us to reuse an already declared variable
class assignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'Assign({self.name} = {self.value})'

class ifNode:
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    def __repr__(self):
        return f'If({self.condition}) Then({self.then_block}) Else({self.else_block})'

class whileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f'While({self.condition} Do({self.body}))'

class forNode:
    def __init__(self, init, condition, update, body):
        self.init      = init
        self.condition = condition
        self.update    = update
        self.body      = body
    def __repr__(self):
        return f'For({self.init}; {self.condition}; {self.update}) Do({self.body})'

class printNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'Print({self.value})'

#Everything inside curly braces
class blockNode:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f'Block({self.statements})'

#This is the root of the entire tree. Everything exist in this node
class programNode:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f'Program({self.statements})'

precedence = (
    #comparison operators are the lowest priority... so it's at the top
    ('left', 'EQUALS', 'NOT_EQUAL'),
    ('left', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'UMINUS'), #unimus is a tag created for negative sign
)

#top of our grammar tree- root rule
def p_program(p):
    '''program : statement_list'''
    p[0] = programNode(p[1])

def p_statement_list_multiple(p): #we start building this list
    '''statement_list : statement_list statement'''
    p[0] = p[1] + [p[2]] 
    #a recursion where a list is added to an existing list
    #builds the list one statement at a time


def p_statement_list_single(p):
    '''statement_list : statement'''
    p[0] = [p[1]]
    #base case for the list

def p_statementVarDecl(p):
    '''statement : DATA_TYPE IDENTIFIER EQUAL_SIGN expression SEMICOLON
                 | DATA_TYPE IDENTIFIER SEMICOLON'''
    if len(p) == 6:
        p[0] = varDeclNode(p[1], p[2], p[4])
    else:
        p[0] = varDeclNode(p[1], p[2])

def p_statementAssign(p):
    '''statement : IDENTIFIER EQUAL_SIGN expression SEMICOLON'''
    p[0] = assignNode(p[1], p[3])

def p_statementIf(p):
    '''statement : IF LPAREN expression RPAREN block
                 | IF LPAREN expression RPAREN block ELSE block
                 | IF LPAREN expression RPAREN THEN block
                 | IF LPAREN expression RPAREN THEN block ELSE block'''
    if len(p) == 6:
        # IF ( expr ) block
        p[0] = ifNode(p[3], p[5])
    elif len(p) == 7:
        # IF ( expr ) THEN block
        p[0] = ifNode(p[3], p[6])
    elif p[6] == 'else':
        # IF ( expr ) block ELSE block
        p[0] = ifNode(p[3], p[5], p[7])
    else:
        # IF ( expr ) THEN block ELSE block
        p[0] = ifNode(p[3], p[6], p[8])

def p_statementWhile(p):
    '''statement : WHILE LPAREN expression RPAREN block'''
    p[0] = whileNode(p[3], p[5])

def p_statementFor(p):
    '''statement : FOR LPAREN for_init SEMICOLON expression SEMICOLON for_update RPAREN block'''
    p[0] = forNode(p[3], p[5], p[7], p[9])

def p_for_init_decl(p):
    '''for_init : DATA_TYPE IDENTIFIER EQUAL_SIGN expression'''
    p[0] = varDeclNode(p[1], p[2], p[4])

def p_for_init_assign(p):
    '''for_init : IDENTIFIER EQUAL_SIGN expression'''
    p[0] = assignNode(p[1], p[3])

def p_for_init_empty(p):
    '''for_init : '''
    p[0] = None

def p_for_update(p):
    '''for_update : IDENTIFIER EQUAL_SIGN expression'''
    p[0] = assignNode(p[1], p[3])

def p_for_update_empty(p):
    '''for_update : '''
    p[0] = None

def p_statementPrint(p):
    '''statement : PRINT LPAREN expression RPAREN SEMICOLON'''
    p[0] = printNode(p[3])

def p_statementExpr(p):
    '''statement : expression SEMICOLON'''
    p[0] = p[1]

def p_block(p):
    '''block : LBRACE statement_list RBRACE 
             | LBRACE RBRACE'''
    if len(p) == 4:
        p[0] = blockNode(p[2])
    else:
        p[0] = blockNode([])

def p_expBinOp(p):
    '''expression : expression PLUS         expression
                  | expression MINUS        expression
                  | expression MULTIPLY     expression
                  | expression DIVIDE       expression
                  | expression EQUALS       expression
                  | expression NOT_EQUAL   expression
                  | expression GREATER_THAN expression
                  | expression GREATER_EQUAL   expression
                  | expression LESS_THAN    expression
                  | expression LESS_EQUAL      expression'''
    p[0] = binaryOpNode(p[1], p[2], p[3])

def p_expUnaryMinus(p):
    '''expression : MINUS expression %prec UMINUS'''
    p[0] = unaryOpNode('-', p[2])

def p_expGroup(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expInt(p):
    '''expression : INT'''
    p[0] = numberNode(p[1])

def p_expFloat(p):
    '''expression : FLOAT'''
    p[0] = numberNode(p[1])

def p_expString(p):
    '''expression : STRING'''
    p[0] = stringNode(p[1])

def p_expBoolean(p):
    '''expression : BOOLEAN'''
    p[0] = booleanNode(p[1] == 'true')

def p_expChar(p):
    '''expression : CHAR'''
    p[0] = charNode(p[1])

def p_expIdentifier(p):
    '''expression : IDENTIFIER'''
    p[0] = identifierNode(p[1])
#variables

def p_error(p):
    if p:
        raise SyntaxError(f"Unexpected token '{p.value}' at line {p.lineno}")
    else:
        raise SyntaxError("Unexpected end of input")
    
class _NullLogger:
    def warning(self, *args, **kwargs): pass
    def error(self,   *args, **kwargs): pass
    def info(self,    *args, **kwargs): pass
    def debug(self,   *args, **kwargs): pass

parser = yacc.yacc(debug=False, write_tables=False, errorlog=_NullLogger())

class parseError(Error):
    def __init__(self, detail):
        super().__init__("Parse Error", detail)

def run(text):
    try:
        ast = parser.parse(text)
        return ast, None
    except SyntaxError as e:
        return None, parseError(str(e))

