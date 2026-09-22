from dataclasses import dataclass
from typing import Any
from core.tokens import TokenType


@dataclass(slots=True)
class ASTNode:
    def accept(self, visitor: Any) -> Any:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(slots=True)
class NumberNode(ASTNode):
    value: int | float

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_number(self)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "NumberNode", "value": self.value}


@dataclass(slots=True)
class VariableNode(ASTNode):
    name: str

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_variable(self)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "VariableNode", "name": self.name}


@dataclass(slots=True)
class UnaryOpNode(ASTNode):
    op: TokenType
    operand: ASTNode

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_unary_op(self)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "UnaryOpNode", "op": self.op.value, "operand": self.operand.to_dict()}


@dataclass(slots=True)
class BinaryOpNode(ASTNode):
    op: TokenType
    left: ASTNode
    right: ASTNode

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_binary_op(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "BinaryOpNode",
            "op": self.op.value,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }


@dataclass(slots=True)
class AssignNode(ASTNode):
    name: str
    value: ASTNode

    def accept(self, visitor: Any) -> Any:
        return visitor.visit_assign(self)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "AssignNode", "name": self.name, "value": self.value.to_dict()}
