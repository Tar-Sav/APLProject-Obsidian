import Obsidian_Parser
from Semantics import SemanticAnalyzer
from Interpreter import Interpreter

analyzer    = SemanticAnalyzer()
interpreter = Interpreter()

print("Obsidian 0.1  |  type 'exit' to quit")

while True:
    try:
        text = input(">> ")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
        break

    if not text.strip():
        continue

    if text.strip() == 'exit':
        print("Exiting.")
        break

    # 1. Parse
    ast, error = Obsidian_Parser.run(text)
    if error:
        print(f"  {error.errorString()}")
        continue

    # 2. Semantic checks (reports all errors before stopping)
    errors = analyzer.analyze(ast)
    if errors:
        for e in errors:
            print(f"  {e.errorString()}")
        continue

    # 3. Interpret
    result, error = interpreter.interpret(ast)
    if error:
        print(f"  {error.errorString()}")
    elif result is not None:
        print(f"  {result}")
