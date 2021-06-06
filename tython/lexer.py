############################################
# LEXER
############################################

from tython.position import Position
from tython.tokens import Token, TokenType
from tython.types.base import Types
from tython.errors import *
import string

WHITESPACE = " \t"
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
SYMBOLS = ".:;"

KEYWORDS = [
    "and",
    "or",
    "not",
    "if",
    ":",
    ";",
    "elif",
    "else",
    "for",
    "to",
    "step",
    "while",
    "def",
    "stop",
]

TYPES = [
    Types.Any.value,
    Types.Number.value,
    Types.Int.value,
    Types.Float.value,
    Types.String.value,
]


class Lexer:
    def __init__(self, fn, text: str):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.advance()
            elif self.current_char in ";\n":
                tokens.append(Token(TokenType.NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS + SYMBOLS:
                for token in self.make_identifier():
                    tokens.append(token)
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == "+":
                tokens.append(Token(TokenType.PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(self.make_minus_arrow())
            elif self.current_char == "*":
                tokens.append(Token(TokenType.MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TokenType.DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TokenType.POWER, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TokenType.LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TokenType.RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TokenType.LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TokenType.RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "!":
                tok, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(tok)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == ",":
                tokens.append(Token(TokenType.COMMA, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TokenType.EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":

            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += self.current_char
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TokenType.INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TokenType.FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        method_str = ""
        pos_start = self.pos.copy()
        dot_start = None
        method_start = None
        tokens = []

        while (
            self.current_char != None
            and self.current_char in LETTERS_DIGITS + "_" + SYMBOLS
        ):
            if self.current_char == ".":
                dot_start = self.pos.copy()
                self.advance()
                method_start = self.pos.copy()
                while self.current_char != None:
                    method_str += self.current_char
                    self.advance()
                break
            id_str += self.current_char
            self.advance()

        if id_str in KEYWORDS:
            tok_type = TokenType.KEYWORD
        elif id_str in TYPES:
            tok_type = TokenType.TYPE
        else:
            tok_type = TokenType.IDENTIFIER

        if dot_start:
            tokens.append(Token(tok_type, id_str, pos_start, dot_start))
            tokens.append(
                Token(TokenType.DOT, pos_start=dot_start, pos_end=method_start)
            )
            if method_str:

                tokens.append(
                    Token(TokenType.METHOD, method_str, method_start, self.pos)
                )

        if len(tokens) > 0:
            return tokens
        return [Token(tok_type, id_str, pos_start, self.pos)]

    def make_string(self):
        string = ""
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {"n": "\n", "t": "\t"}

        while self.current_char != None and (
            self.current_char != '"' or escape_character
        ):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)

            else:
                if self.current_char == "\\":
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        self.advance()
        return Token(TokenType.STRING, string, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TokenType.NE, pos_start=pos_start), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TokenType.EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TokenType.EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TokenType.LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TokenType.LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TokenType.GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TokenType.GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_minus_arrow(self):
        tok_type = TokenType.MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == ">":
            self.advance()
            tok_type = TokenType.ARROW

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
