############################################
# TOKENS
############################################

from enum import Enum
from dataclasses import dataclass
from .runtime.types import Types


class TokenType(Enum):
    NUMBER = "NUMBER"
    INT = "INT"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    KEYWORD = "KEYWORD"
    TYPE = "TYPE"
    IDENTIFIER = "IDENTIFIER"
    EQ = "EQ"
    EE = "EE"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    EOF = "EOF"


KEYWORDS = ["and", "or", "not"]
TYPES = [Types.Int.value, Types.Float.value, Types.String.value]


@dataclass
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

    def __repr__(self):
        return self.type.name + (f":{self.value}" if self.value != None else "")

    def matches(self, type_, value):
        return self.type == type_ and self.value == value
