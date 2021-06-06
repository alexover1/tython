from tython.types.base import Types
from tython.types.Number import Number


class Int(Number):
    """
    Defines the Integer class, which is a number with no decimal places
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
