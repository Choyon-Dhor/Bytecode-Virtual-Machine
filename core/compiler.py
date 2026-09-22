from typing import Any
from core.ast_nodes import ASTNode, NumberNode, VariableNode, UnaryOpNode, BinaryOpNode, AssignNode
from core.opcodes import Instruction, OpCode
from core.tokens import TokenType
from core.exceptions import CompilerError

BINARY_OP_MAP = {
    TokenType.PLUS: OpCode.ADD,
    TokenType.MINUS: OpCode.SUB,
    TokenType.MULTIPLY: OpCode.MUL,
    TokenType.DIVIDE: OpCode.DIV,
    TokenType.POWER: OpCode.POW,
}


class Compiler:
    __slots__ = ("instructions",)

    def __init__(self):
        self.instructions: list[Instruction] = []

    def compile(self, node: ASTNode) -> list[Instruction]:
        self.instructions.clear()
        self._walk(node)
        self.emit(OpCode.HALT)

        for offset, instr in enumerate(self.instructions):
            instr.offset = offset

        return list(self.instructions)

    def emit(self, opcode: OpCode, arg: Any = None) -> Instruction:
        instr = Instruction(opcode=opcode, arg=arg)
        self.instructions.append(instr)
        return instr

    def _walk(self, node: ASTNode) -> None:
        match node:
            case NumberNode(val):
                self.emit(OpCode.LOAD_CONST, val)
            case VariableNode(name):
                self.emit(OpCode.LOAD_VAR, name)
            case UnaryOpNode(TokenType.MINUS, operand):
                self._walk(operand)
                self.emit(OpCode.NEG)
            case UnaryOpNode(TokenType.PLUS, operand):
                self._walk(operand)
            case UnaryOpNode(op, _):
                raise CompilerError(f"Unsupported unary operator: {op}")
            case BinaryOpNode(op, lhs, rhs):
                self._walk(lhs)
                self._walk(rhs)
                if opcode := BINARY_OP_MAP.get(op):
                    self.emit(opcode)
                else:
                    raise CompilerError(f"Unsupported binary operator: {op}")
            case AssignNode(name, value):
                self._walk(value)
                self.emit(OpCode.STORE_VAR, name)
            case _:
                raise CompilerError(f"Unsupported AST node: {type(node).__name__}")

    # Aliases for AST visitor dispatch compatibility
    def visit_number(self, n: NumberNode) -> None: self._walk(n)
    def visit_variable(self, n: VariableNode) -> None: self._walk(n)
    def visit_unary_op(self, n: UnaryOpNode) -> None: self._walk(n)
    def visit_binary_op(self, n: BinaryOpNode) -> None: self._walk(n)
    def visit_assign(self, n: AssignNode) -> None: self._walk(n)

    @staticmethod
    def disassemble(instructions: list[Instruction]) -> str:
        lines = [f"{'OFFSET':<8} {'OPCODE':<14} {'ARGUMENT'}", "-" * 36]
        lines.extend(instr.disassemble() for instr in instructions)
        return "\n".join(lines)
