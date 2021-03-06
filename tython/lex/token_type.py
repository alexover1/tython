from enum import Enum


class TokenType(Enum):
    NUMBER = "NUMBER"
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LSQUARE = "LSQUARE"
    RSQUARE = "RSQUARE"
    KEYWORD = "KEYWORD"
    TYPE = "TYPE"
    IDENTIFIER = "IDENTIFIER"
    DOT = "DOT"
    METHOD = "METHOD"
    EQ = "EQ"
    EE = "EE"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    COMMA = "COMMA"
    ARROW = "ARROW"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
