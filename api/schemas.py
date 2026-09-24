from typing import Any
from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    expression: str
    environment: dict[str, int | float] | None = None


class TokenDTO(BaseModel):
    type: str
    value: Any
    line: int
    column: int
    position: int


class InstructionDTO(BaseModel):
    offset: int
    opcode: str
    arg: Any = None
    description: str = ""


class TraceStepDTO(BaseModel):
    step: int
    ip: int
    instruction: dict[str, Any]
    stack_before: list[int | float]
    stack_after: list[int | float]
    environment: dict[str, int | float]
    action: str


class MetricsDTO(BaseModel):
    execution_time_us: float
    instruction_count: int
    peak_stack_depth: int


class EvaluateResponse(BaseModel):
    success: bool = True
    result: int | float
    tokens: list[TokenDTO]
    ast: dict[str, Any]
    bytecode: list[InstructionDTO]
    disassembly: str
    rpn: list[str]
    trace: list[TraceStepDTO]
    environment: dict[str, int | float]
    metrics: MetricsDTO


class ErrorResponse(BaseModel):
    success: bool = False
    error_type: str
    message: str
    line: int | None = None
    column: int | None = None
    position: int | None = None
    diagnostic: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    engine: str
