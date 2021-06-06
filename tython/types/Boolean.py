from tython.types.base import Value, Types


class Boolean(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.type = Types.Boolean

    def __repr__(self) -> str:
        return (
            f"True <{self.type.name}>"
            if self.value == 1
            else f"False <{self.type.name}>"
        )

    def copy(self):
        copy = Boolean(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
