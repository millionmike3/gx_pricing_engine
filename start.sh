#!/bin/bash
uvicorn backend.api-gateway.server:app --host 0.0.0.0 --port $PORT
