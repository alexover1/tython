############################################
# STRING WITH ARROWS
############################################


def string_with_arrows(text, pos_start, pos_end):
    result = ""

    # Calculate indices
    idx_start = max(text.rfind("\n", 0, pos_start.idx), 0)
    idx_end = text.find("\n", idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * col_start + "^" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")


############################################
# ERRORS
############################################

from enum import Enum


class Errors(Enum):
    IllegalCharError = "IllegalCharError"
    ExpectedCharError = "ExpectedCharError"
    SyntaxError = "SyntaxError"
    RuntimeError = "RuntimeError"
    TypeError = "TypeError"


class Error:
    def __init__(self, pos_start, pos_end, type_, details: str):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.type = type_
        self.details = details

    def __repr__(self) -> str:
        result = f"{self.type}: {self.details}\n"
        result += f"File '{self.pos_start.fn}', line {self.pos_start.ln + 1}"
        result += "\n\n" + string_with_arrows(
            self.pos_start.ftxt, self.pos_start, self.pos_end
        )
        return result


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details: str):
        super().__init__(pos_start, pos_end, Errors.IllegalCharError, details)


class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details: str):
        super().__init__(pos_start, pos_end, Errors.ExpectedCharError, details)


class SyntaxError(Error):
    def __init__(self, pos_start, pos_end, details: str):
        super().__init__(pos_start, pos_end, Errors.SyntaxError, details)
