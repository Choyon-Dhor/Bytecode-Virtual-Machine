class EvaluationError(Exception):
    def __init__(self, message: str, position: int | None = None, line: int = 1, column: int = 1):
        super().__init__(message)
        self.message = message
        self.position = position
        self.line = line
        self.column = column

    def format_diagnostic(self, source: str) -> str:
        lines = source.splitlines()
        if not lines:
            return f"Error: {self.message}"

        line_idx = max(0, min(self.line - 1, len(lines) - 1))
        col_offset = max(0, self.column - 1)
        return (
            f"Error at Line {self.line}, Column {self.column}:\n"
            f"  {lines[line_idx]}\n"
            f"  {' ' * col_offset}^\n"
            f"{type(self).__name__}: {self.message}"
        )


class LexerError(EvaluationError): pass
class ParserError(EvaluationError): pass
class CompilerError(EvaluationError): pass
class VMError(EvaluationError): pass


class DivisionByZeroError(VMError):
    def __init__(self, message: str = "Division by zero is undefined"):
        super().__init__(message)


class StackUnderflowError(VMError):
    def __init__(self, message: str = "Stack underflow: attempted to pop from empty stack"):
        super().__init__(message)


class UndefinedVariableError(VMError):
    def __init__(self, variable_name: str):
        super().__init__(f"Undefined variable: '{variable_name}'")
        self.variable_name = variable_name
