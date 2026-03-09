import ply.lex as lex
import Error

#List of toke names
tokens = ('INT',
          'FLOAT',
          'STRING',
          'CHAR',
          'PLUS',
          'MINUS',
          'MULTIPLY',
          'DIVIDE',
          'LPAREN',
          'RPAREN',
          'LBRACE',
          'RBRACE',
          'EQUAL_SIGN',
          'ID',
          'EQUALS',
          'GREATER_THAN',
          'LESS_THAN',
          'IF',
          'ELSE',
          'THEN',
          'TRY',
          'CATCH',
          'LET',
          'AND',
          'OR',
          'DO'
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
            'try':'TRY',
            'catch':'CATCH',
            'let':'LET',
            'display':'DISPLAY',
            'and' : 'AND',
            'or' : 'OR',
            'do': 'DO'
            }


def t_STRING(t):
    r'\"(.*?)\"'
    t.value = t.value[1:-1]
    return t

def t_CHAR(t):
    r'\'.\''
    t.value = t.value[1:-1]
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    keyword_type = reserved.get(t.value)
    if keyword_type:
        t.type = keyword_type
    else:
        t.type = 'ID'
    return t

def t_COMMENT(t):
    r'--(.*?)\n'
    pass

t_ignore  = ' \t'

def t_error(t):
    Error.IllegalToken(t.value)
    t.lexer.skip(1)

lexer = lex.lex()
