"""Unit tests for the Bytecode Compiler and Disassembler."""

import pytest
from core.lexer import Lexer
from core.parser import Parser
from core.compiler import Compiler
from core.opcodes import OpCode


def compile_expr(expr: str):
    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()
    compiler = Compiler()
    return compiler.compile(ast)


def test_compiler_constants():
    bc = compile_expr("42")
    assert len(bc) == 2
    assert bc[0].opcode == OpCode.LOAD_CONST and bc[0].arg == 42 and bc[0].offset == 0
    assert bc[1].opcode == OpCode.HALT and bc[1].offset == 1


def test_compiler_binary_op():
    bc = compile_expr("2 + 3")
    opcodes = [i.opcode for i in bc]
    assert opcodes == [OpCode.LOAD_CONST, OpCode.LOAD_CONST, OpCode.ADD, OpCode.HALT]
    assert bc[0].arg == 2
    assert bc[1].arg == 3


def test_compiler_unary_negation():
    bc = compile_expr("-5")
    opcodes = [i.opcode for i in bc]
    assert opcodes == [OpCode.LOAD_CONST, OpCode.NEG, OpCode.HALT]
    assert bc[0].arg == 5


def test_compiler_right_associative_power():
    bc = compile_expr("2 ^ 3 ^ 2")
    opcodes = [i.opcode for i in bc]
    # 2, 3, 2, POW, POW, HALT
    assert opcodes == [
        OpCode.LOAD_CONST,
        OpCode.LOAD_CONST,
        OpCode.LOAD_CONST,
        OpCode.POW,
        OpCode.POW,
        OpCode.HALT,
    ]
    assert [i.arg for i in bc[:3]] == [2, 3, 2]


def test_compiler_assignment():
    bc = compile_expr("x = 10")
    opcodes = [i.opcode for i in bc]
    assert opcodes == [OpCode.LOAD_CONST, OpCode.STORE_VAR, OpCode.HALT]
    assert bc[0].arg == 10
    assert bc[1].arg == "x"


def test_disassembly_format():
    bc = compile_expr("2 + 3")
    dis = Compiler.disassemble(bc)
    assert "OFFSET" in dis
    assert "LOAD_CONST" in dis
    assert "ADD" in dis
    assert "HALT" in dis
