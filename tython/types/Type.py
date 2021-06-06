from tython.types.base import Value, Types


class Type(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.Type

    def __repr__(self) -> str:
        return f"<{self.value.name}>"

    def copy(self):
        copy = Type(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
