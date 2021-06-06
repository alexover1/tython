from tython.types.base import Value, Types
from tython.errors import RuntimeError


class Number(Value):
    """
    Either an int or a float
    """

    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.Number

    def __repr__(self) -> str:
        return f"{self.value} <{self.type.name}>"

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

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

    def compare_eq(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value == other.value)).set_context(self.context),
                None,
            )

    def compare_ne(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value != other.value)).set_context(self.context),
                None,
            )

    def compare_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def compare_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def compare_lte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value <= other.value)).set_context(self.context),
                None,
            )

    def compare_gte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value >= other.value)).set_context(self.context),
                None,
            )

    def and_(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value and other.value)).set_context(self.context),
                None,
            )

    def or_(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value or other.value)).set_context(self.context),
                None,
            )

    def not_(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def is_true(self):
        return self.value != 0
