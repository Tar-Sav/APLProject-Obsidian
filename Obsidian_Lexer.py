import ply.lex as lex

#List of toke names
tokens = ('INT',
          'FLOAT',
          'STRING',
          'CHAR',
          'BOOLEAN',
          'PLUS',
          'MINUS',
          'MULTIPLY',
          'DIVIDE',
          'LPAREN',
          'RPAREN',
          'LBRACE',
          'RBRACE',
          'EQUAL_SIGN',
          'IDENTIFIER',
          'EQUALS',
          'GREATER_THAN',
          'LESS_THAN',
          'DATA_TYPE',
          'IF',
          'ELSE',
          'THEN',
          'WHILE',
          'DO',
          'FOR'
          )
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_RBRACE = r'\}'
t_LBRACE = r'\{'
t_EQUAL_SIGN = r'='
t_EQUALS = r'\=='
t_GREATER_THAN = r'>'
t_LESS_THAN = r'<'

reserved = {'if':'IF',
            'then':'THEN',
            'else':'ELSE',
            'while':'WHILE',
            'for':'FOR',
            'int':'DATA_TYPE',
            'float':'DATA_TYPE',
            'char':'DATA_TYPE',
            'bool':'DATA_TYPE',
            'string':'DATA_TYPE',
            }

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'\d+'
    t.value = float(t.value)
    return t
def t_STRING(t):
    r'\"(.*?)\"'
    t.value = t.value
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    keyword_type = reserved.get(t.value)
    if keyword_type:
        t.type = keyword_type
    else:
        t.type = 'IDENTIFIER'
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()
data = r'while(x > 9){}'

lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok.type, tok.value)