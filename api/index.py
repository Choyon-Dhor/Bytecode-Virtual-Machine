"""Vercel Serverless Function entrypoint for FastAPI."""

import sys
from pathlib import Path

# Ensure repository root is on sys.path in Vercel's serverless environment
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.main import app

# Vercel's Python runtime invokes the ASGI `app` callable
__all__ = ["app"]
