#!/bin/bash
export PYTHONPATH=/app/backend
python -m uvicorn backend.api_gateway.server:app --host 0.0.0.0 --port ${PORT}
