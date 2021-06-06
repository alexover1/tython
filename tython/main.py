############################################
# RUN
############################################

from tython.types.Null import Null
from tython.types.Boolean import Boolean
from tython.lexer import Lexer
from tython.parser import Parser
from tython.context import Context, SymbolTable
from tython.interpreter import Interpreter

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Null())
global_symbol_table.set("true", Boolean(1))
global_symbol_table.set("false", Boolean(0))


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
