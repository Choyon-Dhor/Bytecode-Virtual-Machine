import sys
import argparse
from core.lexer import Lexer
from core.parser import Parser
from core.compiler import Compiler
from core.vm import VirtualMachine
from core.exceptions import EvaluationError

BANNER = """Custom Bytecode VM & Math Expression Evaluator
Type an expression or :dis, :rpn, :vars, :clear, :help, exit"""


def run_repl(show_disassembly: bool = False, show_rpn: bool = False) -> None:
    print(BANNER)
    vm = VirtualMachine()
    compiler = Compiler()

    while True:
        try:
            line = input("eval> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not line:
            continue

        match line.lower():
            case "exit" | "quit" | ":q":
                break
            case ":dis":
                show_disassembly = not show_disassembly
                print(f"[REPL] Disassembly {'ON' if show_disassembly else 'OFF'}")
                continue
            case ":rpn":
                show_rpn = not show_rpn
                print(f"[REPL] RPN {'ON' if show_rpn else 'OFF'}")
                continue
            case ":vars":
                if not vm.environment:
                    print("[REPL] No variables defined.")
                else:
                    for k, v in sorted(vm.environment.items()):
                        print(f"  {k:<12} = {v}")
                continue
            case ":clear":
                vm.environment.clear()
                print("[REPL] Environment cleared.")
                continue
            case ":help":
                print(BANNER)
                continue

        try:
            tokens = Lexer(line).tokenize()
            parser = Parser(tokens)

            if show_rpn:
                print(f"[RPN] {' '.join(parser.to_rpn_strings())}")

            ast = parser.parse()
            bytecode = compiler.compile(ast)

            if show_disassembly:
                print(compiler.disassemble(bytecode))

            res = vm.run(bytecode, record_trace=True)
            print(f"=> {res}")

        except EvaluationError as err:
            print(f"\n{err.format_diagnostic(line)}\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Bytecode VM Evaluator REPL")
    p.add_argument("--dis", action="store_true", help="Show bytecode disassembly")
    p.add_argument("--rpn", action="store_true", help="Show RPN tokens")
    args = p.parse_args()
    run_repl(show_disassembly=args.dis, show_rpn=args.rpn)


if __name__ == "__main__":
    main()
