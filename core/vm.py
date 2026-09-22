import time
from dataclasses import dataclass
from typing import Any
from core.opcodes import Instruction, OpCode
from core.exceptions import (
    DivisionByZeroError,
    StackUnderflowError,
    UndefinedVariableError,
    VMError,
)


@dataclass(slots=True)
class TraceStep:
    step: int
    ip: int
    instruction: dict[str, Any]
    stack_before: list[int | float]
    stack_after: list[int | float]
    environment: dict[str, int | float]
    action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "ip": self.ip,
            "instruction": self.instruction,
            "stack_before": list(self.stack_before),
            "stack_after": list(self.stack_after),
            "environment": dict(self.environment),
            "action": self.action,
        }


class VirtualMachine:
    __slots__ = ("stack", "environment", "ip", "trace", "peak_stack_depth", "execution_time_us")

    def __init__(self, environment: dict[str, int | float] | None = None):
        self.stack: list[int | float] = []
        self.environment: dict[str, int | float] = dict(environment) if environment else {}
        self.ip = 0
        self.trace: list[TraceStep] = []
        self.peak_stack_depth = 0
        self.execution_time_us = 0.0

    def push(self, val: int | float) -> None:
        self.stack.append(val)
        if len(self.stack) > self.peak_stack_depth:
            self.peak_stack_depth = len(self.stack)

    def pop(self) -> int | float:
        if not self.stack:
            raise StackUnderflowError("Execution stack underflow: attempted to pop from empty stack")
        return self.stack.pop()

    def run(self, instructions: list[Instruction], record_trace: bool = True) -> int | float:
        self.stack.clear()
        self.trace.clear()
        self.ip = 0
        self.peak_stack_depth = 0

        t0 = time.perf_counter()
        step = 0

        while self.ip < len(instructions):
            instr = instructions[self.ip]
            current_ip = self.ip
            before = list(self.stack)

            match instr.opcode:
                case OpCode.LOAD_CONST:
                    self.push(instr.arg)
                    action = f"Push constant {instr.arg} onto stack"
                    self.ip += 1

                case OpCode.LOAD_VAR:
                    name = str(instr.arg)
                    if name not in self.environment:
                        raise UndefinedVariableError(name)
                    val = self.environment[name]
                    self.push(val)
                    action = f"Load variable '{name}' ({val}) onto stack"
                    self.ip += 1

                case OpCode.STORE_VAR:
                    if not self.stack:
                        raise StackUnderflowError(f"Cannot store into '{instr.arg}': stack is empty")
                    # Assignment evaluates to the assigned value; keep it on top of stack
                    val = self.stack[-1]
                    name = str(instr.arg)
                    self.environment[name] = val
                    action = f"Store top of stack ({val}) into variable '{name}'"
                    self.ip += 1

                case OpCode.ADD:
                    b, a = self.pop(), self.pop()
                    res = a + b
                    self.push(res)
                    action = f"Add: {a} + {b} = {res}"
                    self.ip += 1

                case OpCode.SUB:
                    b, a = self.pop(), self.pop()
                    res = a - b
                    self.push(res)
                    action = f"Subtract: {a} - {b} = {res}"
                    self.ip += 1

                case OpCode.MUL:
                    b, a = self.pop(), self.pop()
                    res = a * b
                    self.push(res)
                    action = f"Multiply: {a} * {b} = {res}"
                    self.ip += 1

                case OpCode.DIV:
                    b, a = self.pop(), self.pop()
                    if b == 0:
                        raise DivisionByZeroError(f"Division by zero: {a} / 0")
                    res = a / b
                    if isinstance(res, float) and res.is_integer():
                        res = int(res)
                    self.push(res)
                    action = f"Divide: {a} / {b} = {res}"
                    self.ip += 1

                case OpCode.POW:
                    b, a = self.pop(), self.pop()
                    res = a ** b
                    if isinstance(res, complex):
                        raise VMError(f"Complex result from exponentiation: {a} ^ {b}")
                    if isinstance(res, float) and res.is_integer():
                        res = int(res)
                    self.push(res)
                    action = f"Exponentiate: {a} ^ {b} = {res}"
                    self.ip += 1

                case OpCode.NEG:
                    a = self.pop()
                    res = -a
                    self.push(res)
                    action = f"Negate: -({a}) = {res}"
                    self.ip += 1

                case OpCode.HALT:
                    action = "Halt execution"
                    self.ip += 1
                    if record_trace:
                        self.trace.append(TraceStep(
                            step=step,
                            ip=current_ip,
                            instruction=instr.to_dict(),
                            stack_before=before,
                            stack_after=list(self.stack),
                            environment=dict(self.environment),
                            action=action,
                        ))
                    break

                case _:
                    raise VMError(f"Unknown OpCode encountered: {instr.opcode}")

            if record_trace and instr.opcode != OpCode.HALT:
                self.trace.append(TraceStep(
                    step=step,
                    ip=current_ip,
                    instruction=instr.to_dict(),
                    stack_before=before,
                    stack_after=list(self.stack),
                    environment=dict(self.environment),
                    action=action,
                ))
            step += 1

        self.execution_time_us = (time.perf_counter() - t0) * 1_000_000.0

        if not self.stack:
            raise VMError("Execution completed with an empty stack; no return value")

        return self.stack[-1]
