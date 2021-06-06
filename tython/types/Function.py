from tython.types.base import Value, Types
from tython.runtime.result import RuntimeResult
from tython.context import Context, SymbolTable


class Function(Value):
    def __init__(self, name, body_node, arg_names, interpreter):
        super().__init__()
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.arg_names = arg_names
        self.type = Types.Function
        self.interpreter = interpreter

    def __repr__(self) -> str:
        return f"{self.name} <{self.type.name}>"

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names, self.interpreter)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute(self, args):
        res = RuntimeResult()
        interpreter = self.interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(  # type:ignore
            new_context.parent.symbol_table  # type:ignore
        )

        if len(args) > len(self.arg_names):
            return res.failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f"too many args ({len(args) - len(self.arg_names)}) passed into '{self.name}'",
                    self.context,
                )
            )

        if len(args) < len(self.arg_names):
            return res.failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f"too few args ({len(self.arg_names) - len(args)}) passed into '{self.name}'",
                    self.context,
                )
            )

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success(value)
