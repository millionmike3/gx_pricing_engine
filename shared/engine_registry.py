import os
import tempfile
from pathlib import Path
from threading import RLock

from shared.matrix_loader import resolve_matrix_path
from shared.pricing_engine import PricingEngine
from shared.pricing_engine_v2 import PricingEngineV2


_lock = RLock()
_engines = None
_active_matrix_path = None


def _build_engines(matrix_path: Path):
    """Build both pricing versions against the same matrix file."""
    path = str(matrix_path)
    return PricingEngine(matrix_path=path), PricingEngineV2(matrix_path=path)


def get_engines(matrix_path=None):
    """Return the active V1/V2 pair, rebuilding if the path changes."""
    global _engines, _active_matrix_path

    path = resolve_matrix_path(matrix_path)

    with _lock:
        if _engines is None or _active_matrix_path != path:
            candidate_engines = _build_engines(path)
            _engines = candidate_engines
            _active_matrix_path = path

        return _engines


def refresh_engines(matrix_path=None):
    """Reload both pricing versions after a successful matrix replacement."""
    global _engines, _active_matrix_path

    path = resolve_matrix_path(matrix_path)

    with _lock:
        candidate_engines = _build_engines(path)
        _engines = candidate_engines
        _active_matrix_path = path

        return _engines



class MatrixActivationError(RuntimeError):
    """Raised when a replaced matrix cannot be activated safely."""


def replace_matrix_and_refresh(temp_path, matrix_path):
    """Atomically replace the matrix and restore it if engine refresh fails."""
    temp_path = Path(temp_path)
    matrix_path = Path(matrix_path)

    previous_bytes = (
        matrix_path.read_bytes() if matrix_path.exists() else None
    )

    os.replace(temp_path, matrix_path)

    try:
        return refresh_engines(matrix_path)
    except Exception as exc:
        rollback_path = None

        try:
            if previous_bytes is None:
                matrix_path.unlink(missing_ok=True)
            else:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    prefix="pricing_matrix_rollback_",
                    suffix=".json",
                    dir=str(matrix_path.parent),
                    delete=False,
                ) as rollback_file:
                    rollback_file.write(previous_bytes)
                    rollback_file.flush()
                    os.fsync(rollback_file.fileno())
                    rollback_path = Path(rollback_file.name)

                os.replace(rollback_path, matrix_path)
                rollback_path = None

        except Exception as rollback_exc:
            raise MatrixActivationError(
                "Engine refresh failed and the previous matrix "
                "could not be restored."
            ) from rollback_exc

        finally:
            if rollback_path is not None:
                rollback_path.unlink(missing_ok=True)

        raise MatrixActivationError(
            "Engine refresh failed. The previous matrix was restored."
        ) from exc
