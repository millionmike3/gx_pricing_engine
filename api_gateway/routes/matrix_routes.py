
import json
import os
import tempfile

from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter(tags=["Matrix"])

# backend/api_gateway/routes/matrix_routes.py
# parents[2] resolves to the backend directory.
BACKEND_DIR = Path(__file__).resolve().parents[2]

# Use Railway's MATRIX_FILE variable if configured.
# Otherwise, default to backend/data/pricing_matrix.json.
configured_path = os.getenv("MATRIX_FILE", "data/pricing_matrix.json")

MATRIX_PATH = Path(configured_path)

if not MATRIX_PATH.is_absolute():
    MATRIX_PATH = BACKEND_DIR / MATRIX_PATH

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


def load_matrix():
    """Load and validate the active pricing matrix file."""

    if not MATRIX_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Pricing matrix file not found."
        )

    try:
        with MATRIX_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Matrix must be a JSON object.")

        return data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Pricing matrix contains invalid JSON."
        )

    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to read pricing matrix."
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get("/current")
def get_current_matrix():
    """
    Returns the currently active pricing matrix.

    Frontend endpoint:
    GET /matrix/current
    """

    data = load_matrix()

    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache"
        }
    )


@router.get("/health")
def matrix_health():
    """Check whether the pricing matrix is available."""

    if not MATRIX_PATH.exists():
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "message": "Pricing matrix file not found."
            }
        )

    try:
        data = load_matrix()

        return {
            "status": "ok",
            "message": "Pricing matrix is available.",
            "sections": list(data.keys())
        }

    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail
            }
        )


@router.post("/upload")
async def upload_matrix(file: UploadFile = File(...)):
    """
    Upload a new pricing matrix.

    Required sections:
    - base_rates
    - adjustments
    - investor_overlays
    """

    content_type = (file.content_type or "").split(";")[0].strip().lower()

    if content_type != "application/json":
        raise HTTPException(
            status_code=400,
            detail="Matrix must be uploaded as application/json."
        )

    contents = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Matrix upload exceeds the 10 MB limit."
        )

    try:
        data = json.loads(contents)

    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file contains invalid JSON."
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="Matrix must be a JSON object."
        )

    required_sections = [
        "base_rates",
        "adjustments",
        "investor_overlays"
    ]

    missing_sections = [
        section for section in required_sections
        if section not in data
    ]

    if missing_sections:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Pricing matrix is missing required sections.",
                "missing_sections": missing_sections
            }
        )

    # Create the destination directory if necessary.
    MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        # Write to a temporary file in the same directory.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            prefix="pricing_matrix_",
            dir=str(MATRIX_PATH.parent),
            delete=False
        ) as temp_file:

            json.dump(
                data,
                temp_file,
                indent=4,
                ensure_ascii=False
            )

            temp_file.flush()
            os.fsync(temp_file.fileno())

            temp_path = Path(temp_file.name)

        # Replace the active matrix atomically.
        os.replace(temp_path, MATRIX_PATH)

        return {
            "status": "ok",
            "message": "Pricing matrix successfully updated.",
            "sections": list(data.keys())
        }

    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to save pricing matrix."
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
