"""Unit tests for the Lexer and Token data structures."""

import pytest
from core.lexer import Lexer
from core.tokens import TokenType
from core.exceptions import LexerError


def test_lexer_integers_and_floats():
    lexer = Lexer("42 3.14 0.5 .75")
    tokens = lexer.tokenize()

    assert len(tokens) == 5  # 4 numbers + EOF
    assert tokens[0].type == TokenType.NUMBER and tokens[0].value == 42
    assert tokens[1].type == TokenType.NUMBER and tokens[1].value == 3.14
    assert tokens[2].type == TokenType.NUMBER and tokens[2].value == 0.5
    assert tokens[3].type == TokenType.NUMBER and tokens[3].value == 0.75
    assert tokens[4].type == TokenType.EOF


def test_lexer_identifiers():
    lexer = Lexer("x radius total_count _temp1")
    tokens = lexer.tokenize()

    assert len(tokens) == 5
    assert tokens[0].type == TokenType.IDENTIFIER and tokens[0].value == "x"
    assert tokens[1].type == TokenType.IDENTIFIER and tokens[1].value == "radius"
    assert tokens[2].type == TokenType.IDENTIFIER and tokens[2].value == "total_count"
    assert tokens[3].type == TokenType.IDENTIFIER and tokens[3].value == "_temp1"
    assert tokens[4].type == TokenType.EOF


def test_lexer_operators_and_delimiters():
    lexer = Lexer("+ - * / ^ = ( )")
    tokens = lexer.tokenize()

    expected_types = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.MULTIPLY,
        TokenType.DIVIDE,
        TokenType.POWER,
        TokenType.ASSIGN,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_lexer_line_and_column_tracking():
    source = "x = 10\ny = 20"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    # Line 1: x = 10
    assert tokens[0].value == "x" and tokens[0].line == 1 and tokens[0].column == 1
    assert tokens[1].type == TokenType.ASSIGN and tokens[1].line == 1 and tokens[1].column == 3
    assert tokens[2].value == 10 and tokens[2].line == 1 and tokens[2].column == 5

    # Line 2: y = 20
    assert tokens[3].value == "y" and tokens[3].line == 2 and tokens[3].column == 1
    assert tokens[4].type == TokenType.ASSIGN and tokens[4].line == 2 and tokens[4].column == 3
    assert tokens[5].value == 20 and tokens[5].line == 2 and tokens[5].column == 5


def test_lexer_malformed_float_error():
    lexer = Lexer("12.34.56")
    with pytest.raises(LexerError) as exc_info:
        lexer.tokenize()
    assert "Malformed floating-point literal" in str(exc_info.value)
    assert exc_info.value.line == 1
    assert exc_info.value.column == 6


def test_lexer_unexpected_character_error():
    lexer = Lexer("2 + @ 3")
    with pytest.raises(LexerError) as exc_info:
        lexer.tokenize()
    assert "Unexpected character: '@'" in str(exc_info.value)
    assert exc_info.value.column == 5


def test_token_serialization():
    lexer = Lexer("123")
    tokens = lexer.tokenize()
    d = tokens[0].to_dict()
    assert d == {
        "type": "NUMBER",
        "value": 123,
        "line": 1,
        "column": 1,
        "position": 0,
    }
