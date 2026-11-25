"""Compatibility entry point for the unified daily matrix validation job."""

try:
    from .daily_ingestion_job import run_daily_ingestion
except ImportError:
    # Also support direct execution from the jobs directory.
    from daily_ingestion_job import run_daily_ingestion


if __name__ == "__main__":
    run_daily_ingestion()
