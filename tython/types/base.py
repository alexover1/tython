from dataclasses import dataclass
from enum import Enum


class Types(Enum):
    Any = "any"
    Null = "null"
    Boolean = "bool"
    Number = "number"
    Int = "int"
    Float = "float"
    Function = "function"
    String = "str"


@dataclass
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def add(self, other):
        return None, self.illegal_operation(other)

    def subtract(self, other):
        return None, self.illegal_operation(other)

    def multiply(self, other):
        return None, self.illegal_operation(other)

    def divide(self, other):
        return None, self.illegal_operation(other)

    def power(self, other):
        return None, self.illegal_operation(other)

    def compare_eq(self, other):
        return None, self.illegal_operation(other)

    def compare_ne(self, other):
        return None, self.illegal_operation(other)

    def compare_lt(self, other):
        return None, self.illegal_operation(other)

    def compare_gt(self, other):
        return None, self.illegal_operation(other)

    def compare_lte(self, other):
        return None, self.illegal_operation(other)

    def compare_gte(self, other):
        return None, self.illegal_operation(other)

    def and_(self, other):
        return None, self.illegal_operation(other)

    def or_(self, other):
        return None, self.illegal_operation(other)

    def not_(self):
        return None, self.illegal_operation()

    def execute(self):
        return None, self.illegal_operation()

    def is_true(self):
        return False

    def copy(self):
        raise Exception("No copy method defined")

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RuntimeError(
            self.pos_start, self.pos_end, "Illegal operation", self.context
        )
