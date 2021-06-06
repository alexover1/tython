from tython.types.base import Types
from tython.types.Number import Number
from tython.types.Boolean import Boolean
from tython.errors import TypeError


class Int(Number):
    """
    Defines the Integer class, which is a Int with no decimal places
    """

    def __init__(self, value):
        super().__init__(value)
        self.type = Types.Int

    def __repr__(self) -> str:
        return f"{self.value} <{self.type.name}>"

    def copy(self):
        copy = Int(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def add(self, other):
        if isinstance(other, Int):
            return Int(self.value + other.value).set_context(self.context), None
        else:
            return None, TypeError(
                self.pos_start, other.pos_end, "Cannot add non Int to Int"
            )

    def subtract(self, other):
        if isinstance(other, Int):
            return Int(self.value - other.value).set_context(self.context), None
        else:
            return None, TypeError(
                self.pos_start, other.pos_end, "Cannot subtract non Int from Int"
            )

    def multiply(self, other):
        if isinstance(other, Int):
            return Int(self.value * other.value).set_context(self.context), None
        else:
            return None, TypeError(
                self.pos_start, other.pos_end, "Cannot multiply non Int and Int"
            )

    def divide(self, other):
        if isinstance(other, Int):
            if other.value == 0:
                return None, RuntimeError(
                    other.pos_start,
                    other.pos_end,
                    "Cannot divide by zero",
                    self.context,
                )
            return Int(self.value / other.value).set_context(self.context), None
        else:
            return None, TypeError(
                self.pos_start, other.pos_end, "Cannot divide Int by non Int"
            )

    def power(self, other):
        if isinstance(other, Int):
            return Int(self.value ** other.value).set_context(self.context), None
        else:
            return None, TypeError(
                self.pos_start, other.pos_end, "Cannot raise Int to non Int"
            )

    def compare_eq(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value == other.value)).set_context(self.context),
                None,
            )

    def compare_ne(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value != other.value)).set_context(self.context),
                None,
            )

    def compare_lt(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value < other.value)).set_context(self.context),
                None,
            )

    def compare_gt(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value > other.value)).set_context(self.context),
                None,
            )

    def compare_lte(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value <= other.value)).set_context(self.context),
                None,
            )

    def compare_gte(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value >= other.value)).set_context(self.context),
                None,
            )

    def and_(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value and other.value)).set_context(self.context),
                None,
            )

    def or_(self, other):
        if isinstance(other, Int):
            return (
                Boolean(int(self.value or other.value)).set_context(self.context),
                None,
            )

    def not_(self):
        return Int(1 if self.value == 0 else 0).set_context(self.context), None
