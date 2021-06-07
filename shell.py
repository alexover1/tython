from tython.main import run
from colorama import init

init(autoreset=True)


while True:
    text = input("> ")
    if text.strip() == "":
        continue
    result, error = run("<stdin>", text)

    if error:
        print(f"\033[31merror \033[0m" + f"{error}")
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
