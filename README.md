# Custom Bytecode Virtual Machine & Math Expression Evaluator

A production-grade, modular, stack-based bytecode virtual machine and mathematical expression evaluator built from scratch in Python 3. 

The core language engine has **zero external dependencies** and does not use `eval()`, `exec()`, or Python's built-in `ast` module. The system includes a **FastAPI backend**, an **interactive single-page web visualizer** with step-by-step stack animation, a **CLI REPL** with live disassembly, and **multi-target deployment configurations** (Vercel, Docker, Render).

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Source Expression / Input |
                      +-----------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Lexer (core/lexer.py)    |
                      | Character-by-character scan |
                      +-----------------------------+
                                     |
                                     v [Token Stream]
                      +-----------------------------+
                      |   Parser (core/parser.py)   |
                      |   Shunting-Yard Infix->RPN  |
                      +-----------------------------+
                                     |
                                     v [Abstract Syntax Tree]
                      +-----------------------------+
                      | Compiler (core/compiler.py) |
                      | Emits linear stack bytecode |
                      +-----------------------------+
                                     |
                                     v [Bytecode Array + HALT]
                      +-----------------------------+
                      | Virtual Machine (core/vm.py)|
                      | LIFO stack & cycle tracer   |
                      +-----------------------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
+-----------------------------+               +-----------------------------+
|    Interactive CLI REPL     |               |    FastAPI REST Backend     |
|         (repl.py)           |               |       (api/main.py)         |
+-----------------------------+               +-----------------------------+
                                                             |
                                                             v
                                              +-----------------------------+
                                              | Interactive Web Visualizer  |
                                              |         (frontend/)         |
                                              +-----------------------------+
```

---

## Key Features

- **Pure Python Core**: Zero external dependencies. Uses only standard library primitives (`dataclasses`, `enum`, `time`, `typing`).
- **Dijkstra's Shunting-Yard Algorithm**:
  - Parses standard infix expressions respecting PEMDAS/BODMAS rules.
  - Supports right-associative exponentiation (`2 ^ 3 ^ 2 == 512`).
  - Supports unary operators and arbitrary nesting (`-5 * 2`, `--5`, `-(3 + 2)`, `2 ^ -3`).
  - Handles single and chained variable assignments (`x = 10`, `x = y = 42`).
- **Stack-based Bytecode Virtual Machine**:
  - Clean LIFO execution model.
  - Cycle-by-cycle **Execution Tracer** capturing stack frames before/after each instruction, environment state, and human-readable operational semantics.
  - Safe domain exceptions: `DivisionByZeroError`, `StackUnderflowError`, `UndefinedVariableError` with visual caret diagnostic indicators (`^`).
- **Interactive Single-Page Visualizer**:
  - Step-by-step visual stack replayer (Push / Pop animations, play/pause controls, slider).
  - Inspection tabs: Lexer Token stream, Bytecode Disassembly table, AST Node hierarchy, and Postfix (RPN) badge queue.
- **Production Web Layer**:
  - FastAPI with Pydantic v2 schemas and HTTP 400 diagnostic error responses.
  - Vercel Serverless Function configuration (`@vercel/python` + Edge CDN static assets).
  - Multi-stage, non-root `Dockerfile` and `docker-compose.yml`.

---

## Directory Structure

```
.
├── core/                       # Zero-Dependency Core Language Engine
│   ├── tokens.py               # TokenType enum and Token dataclass (slots=True)
│   ├── exceptions.py           # Domain exceptions with caret pointer diagnostics
│   ├── lexer.py                # Character scanner with line & column offsets
│   ├── ast_nodes.py            # AST node models (slots=True) with JSON serialization
│   ├── parser.py               # Shunting-Yard parser producing RPN and AST
│   ├── opcodes.py              # OpCode enum, descriptions, and Instruction dataclass
│   ├── compiler.py             # AST-to-bytecode compiler and disassembler
│   ├── vm.py                   # Stack Virtual Machine with execution tracer
│   └── evaluator.py            # Unified end-to-end evaluation pipeline
├── api/                        # FastAPI Web API Layer
│   ├── schemas.py              # Pydantic v2 validation models
│   ├── main.py                 # FastAPI application routes & static file serving
│   └── index.py                # Vercel serverless function entrypoint
├── frontend/                   # Interactive Single-Page Visualizer
│   ├── index.html              # Modern dark-mode layout with multi-tab inspector
│   ├── style.css               # Cyber-terminal styling and animations
│   └── app.js                  # Dynamic stack animator and API client
├── tests/                      # Automated Pytest Suite (44 tests, 100% pass)
│   ├── test_lexer.py           # Literal scanning, identifiers, error positions
│   ├── test_parser.py          # Operator precedence, associativity, AST generation
│   ├── test_compiler.py        # Opcode generation, operand tracking, disassembly
│   ├── test_vm.py              # Stack operations, arithmetic, tracer, domain exceptions
│   ├── test_api.py             # Endpoints, schema validation, static serving
│   └── test_integration.py     # End-to-end evaluation, chained assignments, REPL sessions
├── repl.py                     # Standalone CLI REPL with --dis flag support
├── vercel.json                 # Vercel deployment configuration
├── Dockerfile                  # Multi-stage lightweight, non-root container
├── docker-compose.yml          # Containerized local testing
├── render.yaml                 # Blueprint for one-click cloud deployment
├── Procfile                    # Process command for cloud hosting platforms
├── requirements.txt            # Production dependencies (FastAPI, Uvicorn, Pydantic)
└── requirements-dev.txt        # Development dependencies (Pytest, HTTPX)
```

---

## Bytecode Instruction Set Architecture (ISA)

| OpCode | Operand | Stack Effect | Description |
| :--- | :--- | :--- | :--- |
| `LOAD_CONST` | `<val>` | `( -> val )` | Pushes constant literal onto the stack |
| `LOAD_VAR` | `<name>` | `( -> val )` | Loads variable value from environment onto stack |
| `STORE_VAR` | `<name>` | `( val -> val )` | Stores top-of-stack into variable environment (evaluates to assigned value) |
| `ADD` | None | `( a, b -> a + b )` | Pops `b` and `a`, pushes `a + b` |
| `SUB` | None | `( a, b -> a - b )` | Pops `b` and `a`, pushes `a - b` |
| `MUL` | None | `( a, b -> a * b )` | Pops `b` and `a`, pushes `a * b` |
| `DIV` | None | `( a, b -> a / b )` | Pops `b` and `a`, pushes `a / b` (raises `DivisionByZeroError` if `b == 0`) |
| `POW` | None | `( a, b -> a ^ b )` | Pops `b` and `a`, pushes `a ^ b` |
| `NEG` | None | `( a -> -a )` | Pops `a`, pushes `-a` |
| `HALT` | None | `( -> )` | Terminates VM execution and yields top of stack |

---

## Operator Precedence & Associativity

| Precedence | Operator | Associativity | Description | Example |
| :---: | :---: | :---: | :--- | :--- |
| **4** | `-u`, `+u` | **Right** | Unary negation / identity | `--5 == 5`, `-5 * 2 == -10` |
| **3** | `^` | **Right** | Exponentiation | `2 ^ 3 ^ 2 == 512` |
| **2** | `*`, `/` | **Left** | Multiplication, Division | `4 * 5 / 2 == 10` |
| **1** | `+`, `-` | **Left** | Addition, Subtraction | `2 + 3 * 4 == 14` |
| **0** | `=` | **Right** | Variable Assignment | `x = y = 10` |

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10 or higher.
- `pip` package manager.

### 2. Installation
Clone or navigate to the repository directory and create a virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt
```

---

## Running the Application

### 1. Interactive CLI REPL
Launch the terminal REPL with optional bytecode disassembly:

```bash
# Standard interactive mode
python repl.py

# With automatic bytecode disassembly enabled
python repl.py --dis

# With Reverse Polish Notation (RPN) display enabled
python repl.py --dis --rpn
```

**REPL Meta Commands**:
- `:dis` - Toggle bytecode disassembly display on/off
- `:rpn` - Toggle RPN queue display on/off
- `:vars` - List all active variables in memory
- `:clear` - Clear the variable environment
- `:help` - Display command help
- `exit` or `quit` - Exit the session

---

### 2. Web API & Interactive Visualizer
Start the local FastAPI server:

```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to access the interactive visualizer.

---

## REST API Reference

### Healthcheck
```http
GET /health
```
**Response (200 OK)**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "engine": "Custom Pure-Python Bytecode VM"
}
```

---

### Evaluate Expression
```http
POST /api/evaluate
Content-Type: application/json
```

**Request Payload**:
```json
{
  "expression": "2 ^ 3 ^ 2",
  "environment": {
    "x": 10
  }
}
```

**Response Payload (200 OK)**:
```json
{
  "success": true,
  "result": 512,
  "tokens": [
    {"type": "NUMBER", "value": 2, "line": 1, "column": 1, "position": 0},
    {"type": "POWER", "value": "^", "line": 1, "column": 3, "position": 2},
    {"type": "NUMBER", "value": 3, "line": 1, "column": 5, "position": 4},
    {"type": "POWER", "value": "^", "line": 1, "column": 7, "position": 6},
    {"type": "NUMBER", "value": 2, "line": 1, "column": 9, "position": 8}
  ],
  "ast": {
    "type": "BinaryOpNode",
    "op": "^",
    "left": {"type": "NumberNode", "value": 2},
    "right": {
      "type": "BinaryOpNode",
      "op": "^",
      "left": {"type": "NumberNode", "value": 3},
      "right": {"type": "NumberNode", "value": 2}
    }
  },
  "bytecode": [
    {"offset": 0, "opcode": "LOAD_CONST", "arg": 2, "description": "Push literal constant onto the execution stack"},
    {"offset": 1, "opcode": "LOAD_CONST", "arg": 3, "description": "Push literal constant onto the execution stack"},
    {"offset": 2, "opcode": "LOAD_CONST", "arg": 2, "description": "Push literal constant onto the execution stack"},
    {"offset": 3, "opcode": "POW", "arg": null, "description": "Pop b, pop a; push (a ^ b)"},
    {"offset": 4, "opcode": "POW", "arg": null, "description": "Pop b, pop a; push (a ^ b)"},
    {"offset": 5, "opcode": "HALT", "arg": null, "description": "Halt execution and yield top of stack"}
  ],
  "disassembly": "OFFSET   OPCODE         ARGUMENT\n------------------------------------\n0000     LOAD_CONST     2\n0001     LOAD_CONST     3\n0002     LOAD_CONST     2\n0003     POW            \n0004     POW            \n0005     HALT           ",
  "rpn": ["2", "3", "2", "^", "^"],
  "trace": [
    {
      "step": 0,
      "ip": 0,
      "instruction": {"offset": 0, "opcode": "LOAD_CONST", "arg": 2},
      "stack_before": [],
      "stack_after": [2],
      "environment": {"x": 10},
      "action": "Push constant 2 onto stack"
    }
  ],
  "environment": {"x": 10},
  "metrics": {
    "execution_time_us": 14.5,
    "instruction_count": 6,
    "peak_stack_depth": 3
  }
}
```

**Error Response (400 Bad Request)**:
```json
{
  "success": false,
  "error_type": "ParserError",
  "message": "Unexpected operator '*' after '+'",
  "line": 1,
  "column": 5,
  "position": 4,
  "diagnostic": "Error at Line 1, Column 5:\n  2 + * 3\n      ^\nParserError: Unexpected operator '*' after '+'"
}
```

---

## Testing

Run the automated test suite with `pytest`:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest --cov=core --cov=api tests/
```

All 44 unit and integration tests validate:
- Lexical scanning of numbers, floats, variables, operators, and illegal characters.
- Dijkstra's Shunting-Yard precedence, right-associativity, and unary negation.
- AST compilation into linear bytecode instructions.
- Stack VM execution, LIFO semantics, cycle snapshots, and custom domain exceptions.
- FastAPI endpoint schemas, error handlers, and static asset serving.

---

## Deployment Options

### 1. Vercel (Serverless)
The project includes a ready-to-deploy [`vercel.json`](vercel.json) and serverless entrypoint [`api/index.py`](api/index.py).

```bash
# Install Vercel CLI (optional)
npm install -g vercel

# Deploy directly
vercel
```

Or connect your GitHub repository directly to Vercel. Vercel automatically detects `vercel.json` and `requirements.txt`.

---

### 2. Docker
Build and run the multi-stage, non-root production container:

```bash
# Build image
docker build -t bytecode-vm .

# Run container
docker run -d -p 8000:8000 --name bytecode_vm_app bytecode-vm
```

Or using Docker Compose:

```bash
docker compose up --build
```

---

### 3. Render / Railway / Fly.io
The project includes [`render.yaml`](render.yaml) and [`Procfile`](Procfile) for one-click PaaS deployment:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

---

## License

MIT License. See [LICENSE](LICENSE) for details.
