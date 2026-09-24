from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.schemas import (
    ErrorResponse,
    EvaluateRequest,
    EvaluateResponse,
    HealthResponse,
    InstructionDTO,
    MetricsDTO,
    TokenDTO,
    TraceStepDTO,
)
from core.evaluator import evaluate
from core.exceptions import EvaluationError

app = FastAPI(title="Bytecode VM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0", engine="Custom Pure-Python Bytecode VM")


@app.post("/api/evaluate", response_model=EvaluateResponse, responses={400: {"model": ErrorResponse}})
def evaluate_expression(req: EvaluateRequest):
    try:
        res = evaluate(req.expression, environment=req.environment)

        token_dtos = [
            TokenDTO(type=t.type.value, value=t.value, line=t.line, column=t.column, position=t.position)
            for t in res.tokens
        ]
        instruction_dtos = [
            InstructionDTO(offset=i.offset, opcode=i.opcode.value, arg=i.arg, description=i.to_dict().get("description", ""))
            for i in res.bytecode
        ]
        trace_dtos = [
            TraceStepDTO(
                step=s.step, ip=s.ip, instruction=s.instruction, stack_before=s.stack_before,
                stack_after=s.stack_after, environment=s.environment, action=s.action
            )
            for s in res.trace
        ]

        return EvaluateResponse(
            success=True,
            result=res.result,
            tokens=token_dtos,
            ast=res.ast.to_dict(),
            bytecode=instruction_dtos,
            disassembly=res.disassembly,
            rpn=res.rpn,
            trace=trace_dtos,
            environment=res.environment,
            metrics=MetricsDTO(
                execution_time_us=round(res.execution_time_us, 2),
                instruction_count=len(res.bytecode),
                peak_stack_depth=max((len(s.stack_after) for s in res.trace), default=0),
            ),
        )

    except EvaluationError as err:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                success=False,
                error_type=type(err).__name__,
                message=err.message,
                line=err.line,
                column=err.column,
                position=err.position,
                diagnostic=err.format_diagnostic(req.expression),
            ).model_dump(),
        )


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")
