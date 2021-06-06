############################################
# INTERPRETER
############################################

from tython.types.base import Types
from tython.nodes import *
from tython.types.Any import Any
from tython.types.Number import Number
from tython.types.Int import Int
from tython.types.Float import Float
from tython.types.String import String
from tython.types.Function import Function
from tython.runtime.result import RuntimeResult
from tython.tokens import TokenType
from tython.errors import RuntimeError, TypeError


class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    ############################################

    def visit_AnyNode(self, node, context):
        return RuntimeResult().success(
            Any(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

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

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.tok.value)
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
        elif node.op_tok.matches(TokenType.KEYWORD, "not"):
            result, error = left.not_(right)
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
        elif node.op_tok.matches(TokenType.KEYWORD, "not"):
            number, error = number.not_()

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

        if node.var_type != value.type and node.var_type != Types.Any:
            if not (
                node.var_type == Types.Number and value.type in (Types.Int, Types.Float)
            ):
                return res.failure(
                    TypeError(
                        node.var_name_tok.pos_start,
                        node.var_name_tok.pos_end,
                        f"Cannot assign variable '{var_name}' <{node.var_type.name}> to variable of type <{value.type.name}>",
                    )
                )

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RuntimeResult()

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_ForNode(self, node, context):
        res = RuntimeResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error:
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error:
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error:
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_FuncDefNode(self, node, context):
        res = RuntimeResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names, Interpreter)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error:
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res
        return res.success(return_value)


interpreter = Interpreter()
