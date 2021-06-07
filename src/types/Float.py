from tython.types.base import Types
from tython.types.Number import Number


class Float(Number):
    """
    Defines the Float class, which is a number with a decimal place
    """

    def __init__(self, value):
        super().__init__(value)
        self.type = Types.Float

    def __repr__(self) -> str:
        return f"{self.value} <{self.type.name}>"

    def copy(self):
        copy = Float(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
