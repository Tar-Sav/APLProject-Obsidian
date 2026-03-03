import Obsidian_Lexer

while True:
    text = input("$")
    result, error = Obsidian_Lexer.run(text)

    if error : print(error.errorString())
    else: print(result)