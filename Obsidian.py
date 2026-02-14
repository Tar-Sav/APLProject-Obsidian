#Tokens
class Token:

    #List of token types
    INT = 'INT'
    FLOAT = 'FLOAT'
    DOUBLE = 'DOUBLE'
    STRING = 'STRING'
    CHAR = 'CHAR'
    BOOLEAN = 'BOOLEAN'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    EQUAL = 'EQUAL'

    def __init__(self, type, value):
        self.type = type
        self.value = value

#Error
class Error:
    def __init__(self, errorName, errorDetail):
        self.errorName = errorName
        self.errorDetail = errorDetail

    def errorString(self):
        string = f"{self.errorName}: {self.errorDetail}"
        return string

class IllegalToken(Error):
    def __init__(self, details):
        super().__init__("Illegal Token", details)

#Lexer

class Lexer:

    LETTERS = "abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGIT = "1234567890"
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.currChar = ''
        self.advance()

    def advance(self):
        self.pos +=1
        if self.pos < len(self.text):
            self.currChar = self.text[self.pos]
        else:
            self.currChar = None

    def getTokens(self):
        tokens = []
        while self.currChar != None:
            if self.currChar == '+':
                tokens.append(Token.PLUS)
                self.advance()
            elif self.currChar == '-':
                tokens.append(Token.MINUS)
                self.advance()
            elif self.currChar == '*':
                tokens.append(Token.MUL)
                self.advance()
            elif self.currChar == '/':
                tokens.append(Token.DIV)
                self.advance()
            elif self.currChar == '=':
                tokens.append(Token.EQUAL)
                self.advance()
            elif self.currChar == '(':
                tokens.append(Token.LPAREN)
                self.advance()
            elif self.currChar == ')':
                tokens.append(Token.RPAREN)
                self.advance()
            elif self.currChar == '{':
                tokens.append(Token.LBRACE)
                self.advance()
            elif self.currChar == '}':
                tokens.append(Token.RBRACE)
                self.advance()
            elif self.currChar in self.DIGIT:
                tokens.append(self.makeNumber())
            elif self.currChar in self.LETTERS:
                tokens.append(self.makeWord())
            elif self.currChar == " ":
                self.advance()
            else:
                char = self.currChar
                self.advance()
                return [], IllegalToken(char)

        return tokens, None

    def makeNumber(self):
        numString = ''
        hasDot = False

        while self.currChar != None and self.currChar in self.DIGIT+'.':
            if self.currChar == '.' and not hasDot:
                hasDot = True
                numString += self.currChar
                self.advance()
            elif self.currChar == '.' and hasDot:
                break
            else:
                numString += self.currChar
                self.advance()
        return numString

    def makeWord(self):
        wordString = ""
        while self.currChar != None and self.currChar in self.LETTERS:
            wordString += self.currChar
            self.advance()
        return wordString

#Run

def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.getTokens()

    return tokens, error
