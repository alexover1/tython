from tython.types.base import Value, Types


class Null(Value):
    def __init__(self):
        super().__init__()
        self.type = Types.Null

    def __repr__(self) -> str:
        return f"\033[34m{self.type.name}\033[0m"

    def copy(self):
        copy = Null()
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
