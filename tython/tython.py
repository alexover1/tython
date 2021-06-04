############################################
# RUN
############################################

from .lexer import Lexer
from .parser import Parser
from .runtime import SymbolTable, Number, Interpreter, Context


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(fn, text: str):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Run program
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table  # type: ignore
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
