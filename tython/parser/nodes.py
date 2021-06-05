############################################
# NODES
############################################


class NumberNode:
    """
    Defines a number node
        ex: INT:5
    """

    def __init__(self, tok):
        self.tok = tok

        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_start

    def __repr__(self) -> str:
        return f"{self.tok}"


class BinOpNode:
    """
    Defines a binary operation node
        ex: (INT:5, PLUS, (INT:3, MUL, INT:7))
    """

    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_start

    def __repr__(self) -> str:
        return f"({self.left_node}, {self.op_tok}, {self.right_node})"


class UnaryOpNode:
    """
    Defines a unary operation node
        ex: (MINUS, INT:3)
    """

    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"
