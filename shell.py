from tython.main import run

while True:
    text = input("> ")
    result, error = run("<stdin>", text)

    if error:
        print(error)
    elif result:
        print(result)
