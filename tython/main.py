############################################
# RUN
############################################

from tython.types.Null import Null
from tython.types.Boolean import Boolean
from tython.types.Function import SystemFunction
from tython.lexer import Lexer, SYMBOLS
from tython.parser import Parser
from tython.context import Context, SymbolTable
from tython.interpreter import Interpreter


global_symbol_table = SymbolTable()
global_symbol_table.set("Null", Null())
global_symbol_table.set("True", Boolean(1))
global_symbol_table.set("False", Boolean(0))
global_symbol_table.set("print", SystemFunction("print"))
global_symbol_table.set("return", SystemFunction("return"))
global_symbol_table.set("input", SystemFunction("input"))
global_symbol_table.set("input_int", SystemFunction("input_int"))
global_symbol_table.set("clear", SystemFunction("clear"))
global_symbol_table.set("type", SystemFunction("type"))


def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    if error:
        return None, error

    # print(tokens)

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
