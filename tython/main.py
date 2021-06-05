############################################
# RUN
############################################

from tython.runtime.types import Number
from .lexer import Lexer
from .parser.parser import Parser
from .context import Context
from .interpreter import Interpreter, SymbolTable

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))
global_symbol_table.set("true", Number(1))
global_symbol_table.set("false", Number(0))


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
    context.symbol_table = global_symbol_table  # type:ignore
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
