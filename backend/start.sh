#!/bin/bash

export PYTHONPATH=/app

python -m uvicorn api_gateway.server:app --host 0.0.0.0 --port ${PORT}
