from tython.lex import TokenType
from tython.errors import SyntaxError
from tython.types import Types
from .parse_result import ParseResult
from .nodes import *


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
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
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

    def statements(self):
        """
        : NEWLINE* statement (NEWLINE+ statement)* NEWLINE*
        """
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TokenType.NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TokenType.NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(
            ListNode(statements, pos_start, self.current_tok.pos_end.copy())
        )

    def statement(self):
        """
        : KEYWORD:return expr?
        : KEYWORD:continue
        : KEYWORD:break
        : expr
        """
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        # KEYWORD:return expr?
        if self.current_tok.matches(TokenType.KEYWORD, "return"):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(
                ReturnNode(expr, pos_start, self.current_tok.pos_start.copy())
            )

        # KEYWORD:continue
        if self.current_tok.matches(TokenType.KEYWORD, "continue"):
            res.register_advancement()
            self.advance()
            return res.success(
                ContinueNode(pos_start, self.current_tok.pos_start.copy())
            )

        # KEYWORD:break
        if self.current_tok.matches(TokenType.KEYWORD, "break"):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_start.copy(),
                    "Expected expression, 'return', 'continue', or 'break'",
                )
            )

        return res.success(expr)

    def expr(self):
        """
        : TYPE:var|int|float|str|num IDENTIFIER EQ expr
        : comp-expr ((KEYWORD:AND|KEYWORD:OR) comp-expr)*
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
        : NOT comp-expr
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
                    "Expected int, float, identifier, '+', '-', '(', or 'not'",
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
        """
        : atom (LPAREN (expr (COMMA expr)*)? RPAREN)?
        """
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
        : INT|FLOAT|NUMBER|STRING|IDENTIFIER
        : LPAREN expr RPAREN
        : list-expr
        : if-expr
        : for-expr
        : while-expr
        : func-def
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

            if self.current_tok.type == TokenType.DOT:
                res.register_advancement()
                self.advance()

                if self.current_tok.type == TokenType.METHOD:
                    print("method")
                else:
                    return res.failure(
                        SyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected method",
                        )
                    )

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

    def list_expr(self):
        """
        : LSQUARE (expr (COMMA expr)*)? RSQUARE
        """
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

    def if_expr(self):
        """
        : KEYWORD:if expr KEYWORD::
            (statement if-expr-b|if-expr-c?)
        | (NEWLINE statements KEYWORD:stop|if-expr-b|if-expr-c)
        """
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("if"))
        if res.error:
            return res
        cases, else_case = all_cases  # type: ignore
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        """
        : KEYWORD:elif expr KEYWORD::
            (statement if-expr-b|if-expr-c?)
        | (NEWLINE statements KEYWORD:stop|if-expr-b|if-expr-c)
        """
        return self.if_expr_cases("elif")

    def if_expr_c(self):
        """
        : KEYWORD:else
            statement
        | (NEWLINE statements KEYWORD:stop)
        """
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TokenType.KEYWORD, "else"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TokenType.NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error:
                    return res
                else_case = (statements, True)

                if self.current_tok.matches(TokenType.KEYWORD, "stop"):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(
                        SyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected 'stop'",
                        )
                    )
            else:
                expr = res.register(self.expr())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TokenType.KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TokenType.KEYWORD, case_keyword):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected '{case_keyword}'",
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

        if self.current_tok.type == TokenType.NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error:
                return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(TokenType.KEYWORD, "stop"):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases  # type: ignore
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases  # type: ignore
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def for_expr(self):
        """
        : KEYWORD:FOR IDENTIFIER EQ expr KEYWORD:TO expr
            (KEYWORD:STEP expr)? KEYWORD::
            statement
        | (NEWLINE statements KEYWORD:stop)
        """
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

        if self.current_tok.type == TokenType.NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_tok.matches(TokenType.KEYWORD, "stop"):
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'stop'",
                    )
                )

            res.register_advancement()
            self.advance()

            return res.success(
                ForNode(var_name, start_value, end_value, step_value, body, True)
            )

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(
            ForNode(var_name, start_value, end_value, step_value, body, False)
        )

    def while_expr(self):
        """
        : KEYWORD:while expr KEYWORD::
            statement
        | (NEWLINE statements KEYWORD:stop)
        """
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

        if self.current_tok.type == TokenType.NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_tok.matches(TokenType.KEYWORD, "stop"):
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected 'stop'",
                    )
                )

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def func_def(self):
        """
        : KEYWORD:def IDENTIFIER?
            LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
            (ARROW expr)
        | (NEWLINE statements KEYWORD:stop)
        """
        res = ParseResult()

        if not self.current_tok.matches(TokenType.KEYWORD, "def"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'def'",
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
                        f"Expected '('",
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TokenType.LPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"Expected identifier or '('",
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
                            f"Expected identifier",
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
                        f"Expected ',' or ')'",
                    )
                )
        else:
            if self.current_tok.type != TokenType.RPAREN:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"Expected identifier or ')'",
                    )
                )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TokenType.ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))

        if self.current_tok.type != TokenType.NEWLINE:
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected '->' or new line",
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if not self.current_tok.matches(TokenType.KEYWORD, "stop"):
            return res.failure(
                SyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"Expected 'stop'",
                )
            )

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

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
