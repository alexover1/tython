from tython.types.String import String
from tython.tokens import Token, TokenType
from tython.errors import SyntaxError
from tython.types.base import Types
from tython.nodes import *

############################################
# PARSE RESULT
############################################


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        """
        Takes in ParseResult and extracts and returns node
        """
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        """
        Takes in node and returns node, None
        """
        self.node = node
        return self

    def failure(self, error):
        """
        Takes node and returns None, error
        """
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


############################################
# PARSER
############################################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.var_type = None
        self.advance()

    def advance(self):
        """
        Increments index and returns token at that position
        """
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TokenType.EOF:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '+', '-', '*', '/', or '^'",
                )
            )
        return res

    ############################################

    def expr(self):
        """
        : KEYWORD:TYPE IDENTIFIER EQ expr
        : comp-expr ((KEYWORD:and|KEYWORD:or) comp-expr)*
        """
        res = ParseResult()

        if self.current_tok.type == TokenType.TYPE:
            type = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TokenType.IDENTIFIER:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier",
                    )
                )

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TokenType.EQ:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '='",
                    )
                )

            if type.matches(TokenType.TYPE, Types.Number.value):
                self.var_type = Types.Number
            elif type.matches(TokenType.TYPE, Types.Int.value):
                self.var_type = Types.Int
            elif type.matches(TokenType.TYPE, Types.Float.value):
                self.var_type = Types.Float
            elif type.matches(TokenType.TYPE, Types.String.value):
                self.var_type = Types.String
            else:
                self.var_type = Types.Any

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr, self.var_type))

        node = res.register(
            self.bin_op(
                self.comp_expr, ((TokenType.KEYWORD, "and"), (TokenType.KEYWORD, "or"))
            )
        )

        if res.error:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected expression",
                )
            )

        return res.success(node)

    def comp_expr(self):
        """
        : NOT comp_expr
        : arith-expr ((EE|LT|GT|LTE|GTE) arith-expr)*
        """
        res = ParseResult()

        if self.current_tok.matches(TokenType.KEYWORD, "not"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_op(
                self.arith_expr,
                (
                    TokenType.EE,
                    TokenType.NE,
                    TokenType.LT,
                    TokenType.GT,
                    TokenType.LTE,
                    TokenType.GTE,
                ),
            )
        )

        if res.error:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected int, float, identifier, '+', '-', '(', or 'not",
                )
            )

        return res.success(node)

    def arith_expr(self):
        """
        term ((PLUS|MINUS) term)*
        """
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    def term(self):
        """
        : factor ((MUL | DIV) factor)*
        """
        return self.bin_op(self.factor, (TokenType.MUL, TokenType.DIV))

    def factor(self):
        """
        : (PLUS|MINUS) factor
        : power
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TokenType.PLUS, TokenType.MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        """
        : call (POWER factor)*
        """
        return self.bin_op(self.call, (TokenType.POWER,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TokenType.LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TokenType.RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        SyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected expression",
                        )
                    )

                while self.current_tok.type == TokenType.COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TokenType.RPAREN:
                    return res.failure(
                        SyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            f"Expected ',' or ')'",
                        )
                    )

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def atom(self):
        """
        : INT|FLOAT|STRING|IDENTIFIER
        : LPAREN expr RPAREN
        : if-expr
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type == TokenType.INT:
            res.register_advancement()
            self.advance()
            return res.success(IntNode(tok, self.var_type))

        elif tok.type == TokenType.FLOAT:
            res.register_advancement()
            self.advance()
            return res.success(FloatNode(tok, self.var_type))

        elif tok.type == TokenType.STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok, self.var_type))

        elif tok.type == TokenType.IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TokenType.LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TokenType.RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ')'",
                    )
                )

        elif tok.type == TokenType.LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        elif tok.matches(TokenType.KEYWORD, "if"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TokenType.KEYWORD, "for"):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TokenType.KEYWORD, "while"):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TokenType.KEYWORD, "def"):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(
            SyntaxError(
                tok.pos_start,
                tok.pos_end,
                "Expected int, float, identifier, '+', '-' or '('",
            )
        )

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TokenType.KEYWORD, "if"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'if'",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TokenType.KEYWORD, ":"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected ':'",
                )
            )

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.matches(TokenType, "elif"):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.matches(TokenType.KEYWORD, ":"):
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"Expected ':'",
                    )
                )

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TokenType.KEYWORD, "else"):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TokenType.KEYWORD, "for"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'for'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TokenType.IDENTIFIER:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected identifier",
                )
            )

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TokenType.EQ:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected '='",
                )
            )

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TokenType.KEYWORD, "to"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'to'",
                )
            )

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TokenType.KEYWORD, "step"):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if not self.current_tok.matches(TokenType.KEYWORD, ":"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected ':'",
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TokenType.KEYWORD, "while"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'while'",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TokenType.KEYWORD, ":"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected ':'",
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TokenType.LSQUARE:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '['"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TokenType.RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected expression or ']'",
                    )
                )

            while self.current_tok.type == TokenType.COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TokenType.RSQUARE:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"Expected ',' or ']'",
                    )
                )

            res.register_advancement()
            self.advance()

        return res.success(
            ListNode(element_nodes, pos_start, self.current_tok.pos_end.copy())
        )

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TokenType.KEYWORD, "def"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'def'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TokenType.IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TokenType.LPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '('",
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TokenType.LPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier or '('",
                    )
                )
        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TokenType.IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TokenType.COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TokenType.IDENTIFIER:
                    return res.failure(
                        SyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected identifier",
                        )
                    )

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TokenType.RPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ',' or ')'",
                    )
                )

        else:
            if self.current_tok.type != TokenType.RPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier or ')'",
                    )
                )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TokenType.ARROW:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected '->'",
                )
            )

        res.register_advancement()
        self.advance()
        node_to_return = res.register(self.expr())
        if res.error:
            return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))

    ############################################

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_a())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
