"""Unit tests for the Stack Virtual Machine, Execution Tracer, and Domain Exceptions."""

import pytest
from core.lexer import Lexer
from core.parser import Parser
from core.compiler import Compiler
from core.vm import VirtualMachine
from core.opcodes import Instruction, OpCode
from core.exceptions import (
    DivisionByZeroError,
    StackUnderflowError,
    UndefinedVariableError,
)


def run_code(expr: str, env=None, vm=None):
    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()
    compiler = Compiler()
    bc = compiler.compile(ast)
    if vm is None:
        vm = VirtualMachine(environment=env)
    return vm.run(bc, record_trace=True), vm


def test_vm_basic_arithmetic():
    res, _ = run_code("10 + 20")
    assert res == 30

    res, _ = run_code("100 - 35")
    assert res == 65

    res, _ = run_code("6 * 7")
    assert res == 42

    res, _ = run_code("40 / 8")
    assert res == 5


def test_vm_exponentiation_right_associative():
    # 2 ^ 3 ^ 2 == 2 ^ 9 == 512
    res, _ = run_code("2 ^ 3 ^ 2")
    assert res == 512


def test_vm_unary_negation():
    res, _ = run_code("-5 * 2")
    assert res == -10

    res, _ = run_code("--5")
    assert res == 5

    res, _ = run_code("-(3 + 2)")
    assert res == -5


def test_vm_variables_and_environment():
    vm = VirtualMachine()
    res, _ = run_code("x = 10", vm=vm)
    assert res == 10
    assert vm.environment["x"] == 10

    res, _ = run_code("y = x * 3 + 5", vm=vm)
    assert res == 35
    assert vm.environment["y"] == 35


def test_vm_division_by_zero():
    with pytest.raises(DivisionByZeroError) as exc_info:
        run_code("10 / 0")
    assert "Division by zero" in str(exc_info.value)

    with pytest.raises(DivisionByZeroError):
        run_code("5 / (2 - 2)")


def test_vm_undefined_variable():
    with pytest.raises(UndefinedVariableError) as exc_info:
        run_code("unknown_var * 2")
    assert "unknown_var" in str(exc_info.value)


def test_vm_stack_underflow():
    vm = VirtualMachine()
    corrupted_instructions = [
        Instruction(OpCode.ADD),  # Cannot ADD with empty stack
        Instruction(OpCode.HALT),
    ]
    with pytest.raises(StackUnderflowError):
        vm.run(corrupted_instructions)


def test_vm_execution_tracer():
    res, vm = run_code("2 + 3")
    assert len(vm.trace) == 4  # LOAD_CONST, LOAD_CONST, ADD, HALT

    step0 = vm.trace[0]
    assert step0.instruction["opcode"] == "LOAD_CONST"
    assert step0.instruction["arg"] == 2
    assert step0.stack_before == []
    assert step0.stack_after == [2]

    step1 = vm.trace[1]
    assert step1.instruction["opcode"] == "LOAD_CONST"
    assert step1.stack_before == [2]
    assert step1.stack_after == [2, 3]

    step2 = vm.trace[2]
    assert step2.instruction["opcode"] == "ADD"
    assert step2.stack_before == [2, 3]
    assert step2.stack_after == [5]

    step3 = vm.trace[3]
    assert step3.instruction["opcode"] == "HALT"
    assert step3.stack_after == [5]
