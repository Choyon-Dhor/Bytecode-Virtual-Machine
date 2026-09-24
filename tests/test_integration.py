

"""End-to-end integration tests for the full language and evaluation pipeline."""

import pytest
from core.evaluator import evaluate
from core.vm import VirtualMachine


def test_integration_pemdas():
    res1 = evaluate("2 + 3 * 4")
    assert res1.result == 14

    res2 = evaluate("(2 + 3) * 4")
    assert res2.result == 20

    res3 = evaluate("10 - 2 * 3 + 8 / 2")
    # 10 - 6 + 4 = 8
    assert res3.result == 8


def test_integration_power_associativity():
    # Right-associativity check
    res = evaluate("2 ^ 3 ^ 2")
    assert res.result == 512

    # Left-associativity override via parentheses
    res_override = evaluate("(2 ^ 3) ^ 2")
    assert res_override.result == 64


def test_integration_unary_operations():
    res1 = evaluate("-5 * 2")
    assert res1.result == -10

    res2 = evaluate("--5")
    assert res2.result == 5

    res3 = evaluate("-(3 + 2)")
    assert res3.result == -5

    res4 = evaluate("2 ^ -3")
    assert res4.result == 0.125


def test_integration_persistent_session():
    vm = VirtualMachine()

    # Step 1: define x
    res1 = evaluate("x = 10", vm=vm)
    assert res1.result == 10
    assert vm.environment["x"] == 10

    # Step 2: define y using x
    res2 = evaluate("y = x * 2 + 5", vm=vm)
    assert res2.result == 25
    assert vm.environment["y"] == 25

    # Step 3: compute final expression using both x and y
    res3 = evaluate("x + y", vm=vm)
    assert res3.result == 35


def test_integration_chained_assignment():
    vm = VirtualMachine()
    res = evaluate("x = y = 50", vm=vm)
    assert res.result == 50
    assert vm.environment["x"] == 50
    assert vm.environment["y"] == 50

    res_sum = evaluate("x + y", vm=vm)
    assert res_sum.result == 100


def test_integration_intermediate_artifacts():
    res = evaluate("radius = 5")
    assert len(res.tokens) == 4  # IDENTIFIER, ASSIGN, NUMBER, EOF
    assert res.ast is not None
    assert len(res.bytecode) > 0
    assert len(res.trace) > 0
    assert "LOAD_CONST" in res.disassembly
    assert "STORE_VAR" in res.disassembly
    assert "radius" in res.rpn
