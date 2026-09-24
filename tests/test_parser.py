"""Unit tests for the Shunting-Yard Parser, RPN conversion, and AST construction."""

import pytest
from core.lexer import Lexer
from core.parser import Parser
from core.ast_nodes import NumberNode, VariableNode, UnaryOpNode, BinaryOpNode, AssignNode
from core.tokens import TokenType
from core.exceptions import ParserError


def parse_to_rpn(expr: str):
    tokens = Lexer(expr).tokenize()
    return Parser(tokens).to_rpn_strings()


def parse_to_ast(expr: str):
    tokens = Lexer(expr).tokenize()
    return Parser(tokens).parse()


def test_shunting_yard_precedence():
    # Multiplicative operators take precedence over additive operators
    assert parse_to_rpn("2 + 3 * 4") == ["2", "3", "4", "*", "+"]
    assert parse_to_rpn("2 * 3 + 4") == ["2", "3", "*", "4", "+"]


def test_shunting_yard_parentheses():
    assert parse_to_rpn("(2 + 3) * 4") == ["2", "3", "+", "4", "*"]
    assert parse_to_rpn("2 * (3 + 4)") == ["2", "3", "4", "+", "*"]


def test_shunting_yard_right_associative_power():
    # 2 ^ 3 ^ 2 must parse as 2 ^ (3 ^ 2) -> RPN: 2 3 2 ^ ^
    assert parse_to_rpn("2 ^ 3 ^ 2") == ["2", "3", "2", "^", "^"]


def test_shunting_yard_unary_operators():
    # Prefix unary minus
    assert parse_to_rpn("-5 * 2") == ["5", "-u", "2", "*"]
    # Nested unary minuses
    assert parse_to_rpn("--5") == ["5", "-u", "-u"]
    # Unary minus with parentheses
    assert parse_to_rpn("-(3 + 2)") == ["3", "2", "+", "-u"]
    # Power with negative exponent
    assert parse_to_rpn("2 ^ -3") == ["2", "3", "-u", "^"]


def test_ast_construction_binary():
    ast = parse_to_ast("2 + 3 * 4")
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, NumberNode) and ast.left.value == 2
    assert isinstance(ast.right, BinaryOpNode)
    assert ast.right.op == TokenType.MULTIPLY
    assert ast.right.left.value == 3
    assert ast.right.right.value == 4


def test_ast_construction_unary():
    ast = parse_to_ast("--5")
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.MINUS
    assert isinstance(ast.operand, UnaryOpNode)
    assert ast.operand.op == TokenType.MINUS
    assert isinstance(ast.operand.operand, NumberNode)
    assert ast.operand.operand.value == 5


def test_ast_construction_assignment():
    ast = parse_to_ast("x = 10 + 5")
    assert isinstance(ast, AssignNode)
    assert ast.name == "x"
    assert isinstance(ast.value, BinaryOpNode)
    assert ast.value.op == TokenType.PLUS


def test_ast_chained_assignment():
    ast = parse_to_ast("x = y = 42")
    assert isinstance(ast, AssignNode)
    assert ast.name == "x"
    assert isinstance(ast.value, AssignNode)
    assert ast.value.name == "y"
    assert isinstance(ast.value.value, NumberNode)
    assert ast.value.value.value == 42


def test_ast_serialization():
    ast = parse_to_ast("x = 10")
    d = ast.to_dict()
    assert d == {
        "type": "AssignNode",
        "name": "x",
        "value": {"type": "NumberNode", "value": 10},
    }


def test_parser_syntax_errors():
    with pytest.raises(ParserError):
        parse_to_ast("")

    with pytest.raises(ParserError):
        parse_to_ast("(2 + 3")

    with pytest.raises(ParserError):
        parse_to_ast("2 + 3)")

    with pytest.raises(ParserError):
        parse_to_ast("2 + * 3")

    with pytest.raises(ParserError):
        parse_to_ast("2 +")

    with pytest.raises(ParserError):
        parse_to_ast("2 3")

    with pytest.raises(ParserError):
        parse_to_ast("2 = 10")  # Left-hand side must be variable
