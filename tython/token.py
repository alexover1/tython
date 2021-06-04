############################################
# TOKENS
############################################

from enum import Enum


class TokenType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EQ = "EQ"
    EE = "EE"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    EOF = "EOF"


KEYWORDS = ["int", "and", "or", "not"]


class Token:
    def __init__(
        self, type_: TokenType, value=None, pos_start=None, pos_end=None
    ) -> None:
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self) -> str:
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"
