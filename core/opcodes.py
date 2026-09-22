from dataclasses import dataclass
from enum import Enum
from typing import Any


class OpCode(str, Enum):
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"
    NEG = "NEG"
    HALT = "HALT"

    def __str__(self) -> str:
        return self.value


OPCODE_DESCRIPTIONS: dict[OpCode, str] = {
    OpCode.LOAD_CONST: "Push literal constant onto the execution stack",
    OpCode.LOAD_VAR: "Load variable value from environment and push onto stack",
    OpCode.STORE_VAR: "Assign top of stack to variable in environment",
    OpCode.ADD: "Pop b, pop a; push (a + b)",
    OpCode.SUB: "Pop b, pop a; push (a - b)",
    OpCode.MUL: "Pop b, pop a; push (a * b)",
    OpCode.DIV: "Pop b, pop a; push (a / b)",
    OpCode.POW: "Pop b, pop a; push (a ^ b)",
    OpCode.NEG: "Pop a; push (-a)",
    OpCode.HALT: "Halt execution and yield top of stack",
}


@dataclass(slots=True)
class Instruction:
    opcode: OpCode
    arg: Any = None
    offset: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "offset": self.offset,
            "opcode": self.opcode.value,
            "arg": self.arg,
            "description": OPCODE_DESCRIPTIONS.get(self.opcode, ""),
        }

    def disassemble(self) -> str:
        arg_str = f"{self.arg!r}" if self.arg is not None else ""
        return f"{self.offset:04d}  {self.opcode.value:<12} {arg_str}"

    def __repr__(self) -> str:
        return self.disassemble()
