from dataclasses import dataclass
from core.lexer import Lexer
from core.parser import Parser
from core.compiler import Compiler
from core.vm import VirtualMachine, TraceStep
from core.tokens import Token
from core.ast_nodes import ASTNode
from core.opcodes import Instruction


@dataclass(slots=True)
class EvaluationResult:
    result: int | float
    tokens: list[Token]
    ast: ASTNode
    bytecode: list[Instruction]
    trace: list[TraceStep]
    environment: dict[str, int | float]
    execution_time_us: float
    disassembly: str
    rpn: list[str]


def evaluate(
    expression: str,
    environment: dict[str, int | float] | None = None,
    vm: VirtualMachine | None = None,
) -> EvaluationResult:
    tokens = Lexer(expression).tokenize()
    parser = Parser(tokens)
    rpn_strings = parser.to_rpn_strings()
    ast = parser.parse()

    compiler = Compiler()
    bytecode = compiler.compile(ast)
    disassembly = compiler.disassemble(bytecode)

    if vm is None:
        vm = VirtualMachine(environment=environment)
    elif environment:
        vm.environment.update(environment)

    result = vm.run(bytecode, record_trace=True)

    return EvaluationResult(
        result=result,
        tokens=tokens,
        ast=ast,
        bytecode=bytecode,
        trace=vm.trace,
        environment=dict(vm.environment),
        execution_time_us=vm.execution_time_us,
        disassembly=disassembly,
        rpn=rpn_strings,
    )
