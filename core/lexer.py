from core.tokens import Token, TokenType
from core.exceptions import LexerError

OPERATOR_MAP = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '^': TokenType.POWER,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '=': TokenType.ASSIGN,
}


class Lexer:
    __slots__ = ("source", "pos", "line", "col", "cur")

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.cur = source[0] if source else None

    @property
    def position(self) -> int:
        return self.pos

    @property
    def column(self) -> int:
        return self.col

    def advance(self) -> None:
        if self.cur == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        self.pos += 1
        self.cur = self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self) -> str | None:
        p = self.pos + 1
        return self.source[p] if p < len(self.source) else None

    def skip_whitespace(self) -> None:
        while self.cur is not None and self.cur.isspace():
            self.advance()

    def scan_number(self) -> Token:
        start_pos, start_col, start_line = self.pos, self.col, self.line
        buf = []
        has_dot = False

        if self.cur == '.':
            has_dot = True
            buf.append("0.")
            self.advance()

        while self.cur is not None and (self.cur.isdigit() or self.cur == '.'):
            if self.cur == '.':
                if has_dot:
                    raise LexerError(
                        "Malformed floating-point literal: unexpected second '.'",
                        position=self.pos,
                        line=self.line,
                        column=self.col,
                    )
                has_dot = True
            buf.append(self.cur)
            self.advance()

        val_str = "".join(buf)
        val = float(val_str) if has_dot else int(val_str)
        return Token(TokenType.NUMBER, val, start_line, start_col, start_pos)

    def scan_identifier(self) -> Token:
        start_pos, start_col, start_line = self.pos, self.col, self.line
        buf = []
        while self.cur is not None and (self.cur.isalnum() or self.cur == '_'):
            buf.append(self.cur)
            self.advance()

        return Token(TokenType.IDENTIFIER, "".join(buf), start_line, start_col, start_pos)

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.cur is not None:
            self.skip_whitespace()
            if self.cur is None:
                break

            char = self.cur
            pos, col, line = self.pos, self.col, self.line

            if char.isdigit() or (char == '.' and (nxt := self.peek()) and nxt.isdigit()):
                tokens.append(self.scan_number())
                continue

            if char.isalpha() or char == '_':
                tokens.append(self.scan_identifier())
                continue

            if op_type := OPERATOR_MAP.get(char):
                tokens.append(Token(op_type, char, line, col, pos))
                self.advance()
                continue

            raise LexerError(f"Unexpected character: '{char}'", position=pos, line=line, column=col)

        tokens.append(Token(TokenType.EOF, None, self.line, self.col, self.pos))
        return tokens
