############################################
# SYMBOL TABLE
############################################


class SymbolTable:
    """
    Stores all variables that have been assigned
    """

    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


############################################
# INTERPRETER
############################################

from tython.runtime.types import *
from tython.runtime.result import RuntimeResult
from tython.tokens import TokenType


class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    ############################################

    def visit_NumberNode(self, node, context):
        return RuntimeResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_IntNode(self, node, context):
        return RuntimeResult().success(
            Int(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_FloatNode(self, node, context):
        return RuntimeResult().success(
            Float(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()

        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TokenType.PLUS:
            result, error = left.add(right)
        elif node.op_tok.type == TokenType.MINUS:
            result, error = left.subtract(right)
        elif node.op_tok.type == TokenType.MUL:
            result, error = left.multiply(right)
        elif node.op_tok.type == TokenType.DIV:
            result, error = left.divide(right)
        elif node.op_tok.type == TokenType.POWER:
            result, error = left.power(right)
        elif node.op_tok.type == TokenType.EE:
            result, error = left.compare_eq(right)
        elif node.op_tok.type == TokenType.NE:
            result, error = left.compare_ne(right)
        elif node.op_tok.type == TokenType.LT:
            result, error = left.compare_lt(right)
        elif node.op_tok.type == TokenType.GT:
            result, error = left.compare_gt(right)
        elif node.op_tok.type == TokenType.LTE:
            result, error = left.compare_lte(right)
        elif node.op_tok.type == TokenType.GTE:
            result, error = left.compare_gte(right)
        elif node.op_tok.matches(TokenType.KEYWORD, "and"):
            result, error = left.and_(right)
        elif node.op_tok.matches(TokenType.KEYWORD, "or"):
            result, error = left.or_(right)
        else:
            result, error = None, None

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TokenType.MINUS:
            number, error = number.multiply(Number(-1))

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(
                RuntimeError(
                    node.pos_start, node.pos_end, f"{var_name} is not defined", context
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)
