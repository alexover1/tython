from tython.types import *
from tython.runtime.result import RuntimeResult
from tython.context import Context, SymbolTable
from tython.errors import RuntimeError
import tython.main as main
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
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, interpreter, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.type = Types.Function
        self.interpreter = interpreter
        self.should_auto_return = should_auto_return

    def __repr__(self) -> str:
        return f"\033[36mFunction\033[0m {self.name}"

    def copy(self):
        copy = Function(
            self.name,
            self.body_node,
            self.arg_names,
            self.interpreter,
            self.should_auto_return,
        )
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def execute(self, args):
        res = RuntimeResult()
        interpreter = self.interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res
        ret_value = (
            (value if self.should_auto_return else None)
            or res.func_return_value
            or Null()
        )
        return res.success(ret_value)


class SystemFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)
        self.type = Types.SystemFunction

    def __repr__(self) -> str:
        return f"\033[36mSystemFunction\033[0m {self.name}"

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
        if res.should_return():
            return res

        return_value = res.register(method(exec_ctx))  # type: ignore
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit_method(self):
        raise Exception(f"No execute_{self.name} method defined")

    ############################################

    def execute_run(self, exec_ctx):
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RuntimeResult().failure(
                RuntimeError(
                    self.pos_start, self.pos_end, "File name must be a string", exec_ctx
                )
            )

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RuntimeResult().failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f'Failed to load script "{fn}"\n' + str(e),
                    exec_ctx,
                )
            )

        _, error = main.run(fn, script)

        if error:
            return RuntimeResult().failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    f'Failed to finish executing script "{fn}"\n' + f"{error}",
                    exec_ctx,
                )
            )

        return RuntimeResult().success(Null())

    execute_run.arg_names = ["fn"]

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

    def execute_input(self, _):
        text = input()
        return RuntimeResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, _):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be of type <Int>")
        return RuntimeResult().success(Int(number))

    execute_input_int.arg_names = []

    def execute_clear(self, _):
        os.system("cls" if os.name == "nt" else "clear")
        return RuntimeResult().success(Null())

    execute_clear.arg_names = []

    def execute_type(self, exec_ctx):
        type_ = exec_ctx.symbol_table.get("value")
        return RuntimeResult().success(Type(type_.type))

    execute_type.arg_names = ["value"]

    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")

        if not isinstance(list_, List):
            return RuntimeResult().failure(
                RuntimeError(
                    self.pos_start,
                    self.pos_end,
                    "Argument must be a \033[34mList\033[0m",
                    exec_ctx,
                )
            )

        return RuntimeResult().success(Int(len(list_.elements)))

    execute_len.arg_names = ["list"]
