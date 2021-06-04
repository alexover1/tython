###########################################
# LEXER
###########################################

from .position import Position
from .token import Token, TokenType, KEYWORDS
from .error import IllegalCharError, ExpectedCharError
import string

DIGITS: str = "0123456789"
LETTERS: str = string.ascii_letters
LETTERS_DIGITS: str = LETTERS + DIGITS


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
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_indetifier())
            elif self.current_char == "+":
                tokens.append(Token(TokenType.PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TokenType.MINUS, pos_start=self.pos))
                self.advance()
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
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TokenType.EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str: str = ""
        dot_count: int = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TokenType.INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TokenType.FLOAT, float(num_str), pos_start, self.pos)

    def make_indetifier(self):
        id_str = ""
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            id_str += self.current_char
            self.advance()

        tok_type = TokenType.KEYWORD if id_str in KEYWORDS else TokenType.IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TokenType.NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' after '!'")

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