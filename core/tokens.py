from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(str, Enum):
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ASSIGN = "ASSIGN"
    EOF = "EOF"

    def __str__(self) -> str:
        return self.value


@dataclass(slots=True, frozen=True)
class Token:
    type: TokenType
    value: Any
    line: int = 1
    column: int = 1
    position: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "value": self.value,
            "line": self.line,
            "column": self.column,
            "position": self.position,
        }

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"
