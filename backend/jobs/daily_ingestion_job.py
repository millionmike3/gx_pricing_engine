import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.matrix_loader import load_matrix, resolve_matrix_path


LOG_PATH = Path(os.getenv("INGEST_LOG", "logs/daily_ingestion.log"))


def run_daily_ingestion():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        matrix = load_matrix()
        timestamp = datetime.now(timezone.utc).isoformat()
        message = (
            f"{timestamp} - Unified matrix validation OK; "
            f"path: {resolve_matrix_path()}; "
            f"FICO tiers: {len(matrix['pricingTiers']['fico'])}; "
            f"LTV tiers: {len(matrix['pricingTiers']['ltv'])}\n"
        )
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(message)
        return {"status": "ok", "message": message.strip()}
    except Exception as exc:
        timestamp = datetime.now(timezone.utc).isoformat()
        message = f"{timestamp} - Ingestion FAILED: {exc}\n"
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(message)
        raise


if __name__ == "__main__":
    run_daily_ingestion()
