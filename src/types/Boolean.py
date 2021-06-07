from tython.types.base import Value, Types


class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.Boolean

    def __repr__(self) -> str:
        return "\033[34mTrue\033[0m" if self.value == 1 else "\033[34mFalse\033[0m"

    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0
