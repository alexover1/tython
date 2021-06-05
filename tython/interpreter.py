############################################
# INTERPRETER
############################################

from .runtime.types import Number
from .runtime.result import RuntimeResult
from .tokens import TokenType


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
