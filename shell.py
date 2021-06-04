from tython.tython import run

while True:
    text = input("> ")
    result, error = run("<stdin>", text)

    if error:
        print(error.as_string())
    else:
        print(result)
