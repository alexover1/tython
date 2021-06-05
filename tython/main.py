############################################
# RUN
############################################

from .lexer import Lexer
from .parser.parser import Parser
from .context import Context
from .interpreter import Interpreter


def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    if error:
        return None, error

    # Generate AST (Abstract Syntax Tree)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Interpret AST
    interpreter = Interpreter()
    context = Context("<program>")
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
