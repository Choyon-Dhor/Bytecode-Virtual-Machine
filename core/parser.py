from dataclasses import dataclass
from typing import Union
from core.tokens import Token, TokenType
from core.ast_nodes import ASTNode, NumberNode, VariableNode, UnaryOpNode, BinaryOpNode, AssignNode
from core.exceptions import ParserError


@dataclass(slots=True, frozen=True)
class OperatorInfo:
    symbol: str
    precedence: int
    right_associative: bool
    arity: int


OPERATORS: dict[Union[TokenType, str], OperatorInfo] = {
    "UNARY_MINUS": OperatorInfo("-u", 4, True, 1),
    "UNARY_PLUS": OperatorInfo("+u", 4, True, 1),
    TokenType.POWER: OperatorInfo("^", 3, True, 2),
    TokenType.MULTIPLY: OperatorInfo("*", 2, False, 2),
    TokenType.DIVIDE: OperatorInfo("/", 2, False, 2),
    TokenType.PLUS: OperatorInfo("+", 1, False, 2),
    TokenType.MINUS: OperatorInfo("-", 1, False, 2),
    TokenType.ASSIGN: OperatorInfo("=", 0, True, 2),
}


class Parser:
    __slots__ = ("tokens",)

    def __init__(self, tokens: list[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.EOF]

    def parse(self) -> ASTNode:
        if not self.tokens:
            raise ParserError("Empty expression cannot be parsed", line=1, column=1, position=0)
        return self._rpn_to_ast(self.to_rpn())

    def to_rpn(self) -> list[Token | OperatorInfo]:
        out_queue: list[Token | OperatorInfo] = []
        op_stack: list[Token | OperatorInfo] = []
        prev_tok: Token | None = None
        is_unary_context = True

        for tok in self.tokens:
            if tok.type == TokenType.NUMBER:
                if prev_tok and prev_tok.type in (TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.RPAREN):
                    raise ParserError(
                        f"Unexpected number literal '{tok.value}' without preceding operator",
                        position=tok.position, line=tok.line, column=tok.column,
                    )
                out_queue.append(tok)
                prev_tok, is_unary_context = tok, False

            elif tok.type == TokenType.IDENTIFIER:
                if prev_tok and prev_tok.type in (TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.RPAREN):
                    raise ParserError(
                        f"Unexpected identifier '{tok.value}' without preceding operator",
                        position=tok.position, line=tok.line, column=tok.column,
                    )
                out_queue.append(tok)
                prev_tok, is_unary_context = tok, False

            elif tok.type in (TokenType.PLUS, TokenType.MINUS):
                op_key = ("UNARY_MINUS" if tok.type == TokenType.MINUS else "UNARY_PLUS") if (
                    is_unary_context or prev_tok is None or prev_tok.type == TokenType.LPAREN
                ) else tok.type
                self._push_op(OPERATORS[op_key], op_stack, out_queue)
                prev_tok, is_unary_context = tok, True

            elif tok.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.POWER, TokenType.ASSIGN):
                if is_unary_context or prev_tok is None or prev_tok.type == TokenType.LPAREN:
                    raise ParserError(
                        f"Unexpected binary operator '{tok.value}' in prefix position",
                        position=tok.position, line=tok.line, column=tok.column,
                    )
                self._push_op(OPERATORS[tok.type], op_stack, out_queue)
                prev_tok, is_unary_context = tok, True

            elif tok.type == TokenType.LPAREN:
                if prev_tok and prev_tok.type in (TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.RPAREN):
                    raise ParserError("Missing operator before '('", position=tok.position, line=tok.line, column=tok.column)
                op_stack.append(tok)
                prev_tok, is_unary_context = tok, True

            elif tok.type == TokenType.RPAREN:
                if is_unary_context:
                    raise ParserError("Unexpected ')' immediately following operator", position=tok.position, line=tok.line, column=tok.column)

                matched = False
                while op_stack:
                    top = op_stack.pop()
                    if isinstance(top, Token) and top.type == TokenType.LPAREN:
                        matched = True
                        break
                    out_queue.append(top)

                if not matched:
                    raise ParserError("Mismatched closing parenthesis ')' without matching '('", position=tok.position, line=tok.line, column=tok.column)
                prev_tok, is_unary_context = tok, False

        if is_unary_context and prev_tok:
            raise ParserError(
                f"Unexpected end of expression after operator '{prev_tok.value}'",
                position=prev_tok.position, line=prev_tok.line, column=prev_tok.column,
            )

        while op_stack:
            top = op_stack.pop()
            if isinstance(top, Token) and top.type == TokenType.LPAREN:
                raise ParserError("Mismatched opening parenthesis '(' without closing ')'", position=top.position, line=top.line, column=top.column)
            out_queue.append(top)

        return out_queue

    def _push_op(self, op: OperatorInfo, op_stack: list[Token | OperatorInfo], out_queue: list[Token | OperatorInfo]) -> None:
        while op_stack:
            top = op_stack[-1]
            if isinstance(top, Token) and top.type == TokenType.LPAREN:
                break

            top_op = top if isinstance(top, OperatorInfo) else OPERATORS.get(top.type)
            if not top_op:
                break

            if (top_op.precedence > op.precedence) or (
                top_op.precedence == op.precedence and not op.right_associative
            ):
                out_queue.append(op_stack.pop())
            else:
                break

        op_stack.append(op)

    def _rpn_to_ast(self, rpn: list[Token | OperatorInfo]) -> ASTNode:
        stack: list[ASTNode] = []

        for item in rpn:
            match item:
                case Token(type=TokenType.NUMBER, value=val):
                    stack.append(NumberNode(val))
                case Token(type=TokenType.IDENTIFIER, value=name):
                    stack.append(VariableNode(name))
                case OperatorInfo(symbol="-u", arity=1):
                    if not stack:
                        raise ParserError("Missing operand for unary operator '-u'")
                    stack.append(UnaryOpNode(TokenType.MINUS, stack.pop()))
                case OperatorInfo(symbol="+u", arity=1):
                    if not stack:
                        raise ParserError("Missing operand for unary operator '+u'")
                    stack.append(UnaryOpNode(TokenType.PLUS, stack.pop()))
                case OperatorInfo(symbol="=", arity=2):
                    if len(stack) < 2:
                        raise ParserError("Missing operands for assignment '='")
                    rhs, lhs = stack.pop(), stack.pop()
                    if not isinstance(lhs, VariableNode):
                        raise ParserError(f"Invalid assignment target: left-hand side must be variable, got {type(lhs).__name__}")
                    stack.append(AssignNode(lhs.name, rhs))
                case OperatorInfo(symbol=sym, arity=2):
                    if len(stack) < 2:
                        raise ParserError(f"Missing operands for binary operator '{sym}'")
                    rhs, lhs = stack.pop(), stack.pop()
                    tok_type = next((t for t, o in OPERATORS.items() if isinstance(t, TokenType) and o.symbol == sym), None)
                    if not tok_type:
                        raise ParserError(f"Unknown operator symbol '{sym}'")
                    stack.append(BinaryOpNode(tok_type, lhs, rhs))
                case _:
                    raise ParserError(f"Unexpected token in RPN: {item}")

        if len(stack) != 1:
            raise ParserError(f"Malformed expression: {len(stack)} unreduced nodes remain on stack")
        return stack[0]

    def to_rpn_strings(self) -> list[str]:
        return [str(item.value) if isinstance(item, Token) else item.symbol for item in self.to_rpn()]
