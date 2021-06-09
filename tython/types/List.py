from tython.types.Number import Number
from tython.types.base import Value, Types
from tython.errors import RuntimeError


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.type = Types.List

    def __repr__(self) -> str:
        elements = ", ".join([str(x) for x in self.elements])
        return f"\033[36mList\033[0m [{elements}]"

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def add(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subtract(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except:
                return None, RuntimeError(
                    self.pos_start, other.pos_end, "Index out of bounds", self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multiply(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def divide(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RuntimeError(
                    self.pos_start, other.pos_end, "Index out of bounds", self.context
                )
        else:
            return None, Value.illegal_operation(self, other)
