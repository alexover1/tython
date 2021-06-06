from tython.types.base import Value, Types
from tython.types.Type import Type
from tython.types.Boolean import Boolean
from tython.types.Null import Null
from tython.types.Int import Int
from tython.types.Float import Float
from tython.types.String import String
from tython.runtime.result import RuntimeResult
from tython.context import Context, SymbolTable
from tython.errors import RuntimeError
import os


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(  # type:ignore
            new_context.parent.symbol_table
        )
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()

        if len(args) > len(arg_names):
            return res.failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f"too many args passed into '{self.name}' (Expected {len(arg_names)}",
                    self.context,
                )
            )

        if len(args) < len(arg_names):
            return res.failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f"too few args passed into '{self.name}' (Expected {len(arg_names)})",
                    self.context,
                )
            )

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.error:
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, interpreter, should_return_null):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.type = Types.Function
        self.interpreter = interpreter
        self.should_return_null = should_return_null

    def __repr__(self) -> str:
        return f"{self.name} <{self.type.name}>"

    def copy(self):
        copy = Function(
            self.name,
            self.body_node,
            self.arg_names,
            self.interpreter,
            self.should_return_null,
        )
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute(self, args):
        res = RuntimeResult()
        interpreter = self.interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.error:
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.error:
            return res
        return res.success(Null() if self.should_return_null else value)


class SystemFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type = Types.SystemFunction

    def __repr__(self) -> str:
        return f"{self.name} <System.Function>"

    def copy(self):
        copy = SystemFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute(self, args):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.error:
            return res

        return_value = res.register(method(exec_ctx))  # type: ignore
        if res.error:
            return res
        return res.success(return_value)

    def no_visit_method(self):
        raise Exception(f"No execute_{self.name} method defined")

    ############################################

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RuntimeResult().success(Null())

    execute_print.arg_names = ["value"]

    def execute_return(self, exec_ctx):
        value = exec_ctx.symbol_table.get("value")
        if isinstance(value, Int):
            return RuntimeResult().success(Int(value.value))
        if isinstance(value, Float):
            return RuntimeResult().success(Float(value.value))
        if isinstance(value, String):
            return RuntimeResult().success(String(value.value))
        if isinstance(value, Boolean):
            return RuntimeResult().success(Boolean(value.value))
        return RuntimeResult().success(String(str(exec_ctx.symbol_table.get("value"))))

    execute_return.arg_names = ["value"]

    def execute_input(self, exec_ctx):
        text = input()
        return RuntimeResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be of type <Int>")
        return RuntimeResult().success(Int(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system("cls" if os.name == "nt" else "clear")
        return RuntimeResult().success(Null())

    execute_clear.arg_names = []

    def execute_type(self, exec_ctx):
        type_ = exec_ctx.symbol_table.get("value")
        return RuntimeResult().success(Type(type_.type))

    execute_type.arg_names = ["value"]
