import Obsidian

while True:
    text = input("$")
    result, error = Obsidian.run(text)

    if error : print(error.errorString())
    else: print(result)