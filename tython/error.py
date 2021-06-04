############################################
# ERRORS
###########################################

from enum import Enum
from .error_string import string_with_arrows


class Errors(Enum):
    IllegalChar = "IllegalChar"
    ExpectedChar = "ExpectedChar"
    SyntaxError = "SyntaxError"
    RuntimeError = "RuntimeError"


class Error:
    def __init__(self, pos_start, pos_end, type_, details) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.type = type_
        self.details = details

    def as_string(self):
        result = f"{self.type}: {self.details}\n"
        result += f"File {self.pos_start.fn}, line {self.pos_start.ln + 1}"
        result += "\n\n" + string_with_arrows(
            self.pos_start.ftxt, self.pos_start, self.pos_end
        )

        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end, Errors.IllegalChar, details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end, Errors.ExpectedChar, details)


class SyntaxError(Error):
    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end, Errors.SyntaxError, details)


class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, details, context) -> None:
        super().__init__(pos_start, pos_end, Errors.RuntimeError, details)
        self.context = context
