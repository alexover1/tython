############################################
# PARSER
############################################

from ..tokens import TokenType
from ..errors import SyntaxError
from .result import ParseResult
from .nodes import NumberNode, BinOpNode, UnaryOpNode


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
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

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TokenType.INT, TokenType.FLOAT, TokenType.NUMBER):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TokenType.LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TokenType.RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(
                    SyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ')'",
                    )
                )

        return res.failure(
            SyntaxError(
                tok.pos_start, tok.pos_end, "Expected int, float, '+', '-' or '('"
            )
        )

    def power(self):
        return self.bin_op(self.atom, (TokenType.POWER,), self.factor)

    def factor(self):
        """
        Looks for int, float, or number, returns ParseResult(NumberNode)
        """
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TokenType.PLUS, TokenType.MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        """
        Looks for mul or div, repeats until no more are found, returns BinOpNode
        """
        return self.bin_op(self.factor, (TokenType.MUL, TokenType.DIV))

    def expr(self):
        """
        Looks for plus or minus, repeats until no more are found, returns BinOpNode
        """
        return self.bin_op(self.term, (TokenType.PLUS, TokenType.MINUS))

    ############################################

    def bin_op(self, func, ops, func_b=None):
        if func_b == None:
            func_b = func

        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)  # ParseResult(BinOpNode)
