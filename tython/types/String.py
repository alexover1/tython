from tython.types.base import Value, Types
from tython.types.Number import Number
from tython.types.Int import Int


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.String

    def __repr__(self) -> str:
        return f'\033[36m{self.type.name}\033[0m "{self.value}"'

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def add(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subtract(self, other):
        if isinstance(other, String):
            return (
                String(self.value.replace(other.value, "")).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def multiply(self, other):
        if isinstance(other, Number) or isinstance(other, Int):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0
