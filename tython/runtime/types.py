from dataclasses import dataclass
from enum import Enum
from typing import Union

from .errors import RuntimeError, TypeError


class Types(Enum):
    Number = Union[int, float]
    Int = int
    Float = float
    String = str


@dataclass
class Number:
    def __init__(self, value, type: Types = Types.Number):
        self.value = value
        self.error = None
        self.type = type
        self.set_pos()
        self.set_context()

    def __repr__(self) -> str:
        return f"{self.value}"

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def add(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, TypeError(
                other.pos_start, other.pos_end, "Cannot add non Number to Number"
            )

    def subtract(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, TypeError(
                other.pos_start, other.pos_end, "Cannot subtract non Number from Number"
            )

    def multiply(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, TypeError(
                other.pos_start, other.pos_end, "Cannot multiply non Number and Number"
            )

    def divide(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start,
                    other.pos_end,
                    "Cannot divide by zero",
                    self.context,
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, TypeError(
                other.pos_start, other.pos_end, "Cannot divide Number by non Number"
            )

    def power(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, TypeError(
                other.pos_start, other.pos_end, "Cannot raise Number to non Number"
            )


@dataclass
class Int(Number):
    def __init__(self, value):
        super().__init__(value, type=Types.Int)
        if type(value) != Types.Int.value:
            # type error
            pass

    def __repr__(self) -> str:
        return f"{self.value}"


@dataclass
class String:
    value: str
    type: Types = Types.String

    def __repr__(self) -> str:
        return f"{self.value}"
