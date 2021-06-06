from tython.types.base import Value, Types
from tython.types.Number import Number
from tython.types.Boolean import Boolean


class Any(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.Any

    def __repr__(self) -> str:
        return f"{self.value} <{self.type.name}>"

    def copy(self):
        copy = Any(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def add(self, other):
        return Number(self.value + other.value).set_context(self.context), None

    def subtract(self, other):
        return Number(self.value - other.value).set_context(self.context), None

    def multiply(self, other):
        return Number(self.value - other.value).set_context(self.context), None

    def divide(self, other):
        if other.value == 0:
            return None, RuntimeError(
                other.pos_start,
                other.pos_end,
                "Cannot divide by zero",
                self.context,
            )
        return Number(self.value / other.value).set_context(self.context), None

    def power(self, other):
        return Number(self.value ** other.value).set_context(self.context), None

    def compare_eq(self, other):
        return (
            Boolean(int(self.value == other.value)).set_context(self.context),
            None,
        )

    def compare_ne(self, other):
        return (
            Boolean(int(self.value != other.value)).set_context(self.context),
            None,
        )

    def compare_lt(self, other):
        return Boolean(int(self.value < other.value)).set_context(self.context), None

    def compare_gt(self, other):
        return Boolean(int(self.value > other.value)).set_context(self.context), None

    def compare_lte(self, other):
        return (
            Boolean(int(self.value <= other.value)).set_context(self.context),
            None,
        )

    def compare_gte(self, other):
        return (
            Boolean(int(self.value >= other.value)).set_context(self.context),
            None,
        )

    def and_(self, other):
        return (
            Number(int(self.value and other.value)).set_context(self.context),
            None,
        )

    def or_(self, other):
        return (
            Number(int(self.value or other.value)).set_context(self.context),
            None,
        )

    def not_(self):
        return Boolean(1 if self.value == 0 else 0).set_context(self.context), None

    def is_true(self):
        return self.value != 0
