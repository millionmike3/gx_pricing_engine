import logging
import os

import psycopg2
from psycopg2.extras import Json, RealDictCursor


logger = logging.getLogger("genxbaby-pricing-engine.activity")


def _connect():
    """Open a PostgreSQL connection without exposing connection credentials."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg2.connect(
        dsn=database_url,
        connect_timeout=5,
    )


def record_activity(
    action,
    module,
    actor_role="ANONYMOUS",
    actor_id=None,
    details=None,
    status="SUCCESS",
    duration_ms=None,
):
    """
    Best-effort activity recording.

    Callers must provide metadata only. Never pass borrower information,
    loan application data, credentials, or complete pricing requests.
    """

    connection = None

    try:
        connection = _connect()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO pricing_engine_activity (
                    actor_role,
                    actor_id,
                    action,
                    module,
                    details,
                    status,
                    duration_ms
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    actor_role,
                    actor_id,
                    action,
                    module,
                    Json(details if isinstance(details, dict) else {}),
                    status,
                    duration_ms,
                ),
            )

        connection.commit()
        return True

    except Exception as exc:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass

        logger.warning(
            "Activity recording unavailable (%s).",
            type(exc).__name__,
        )
        return False

    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


def fetch_recent_activity(limit=50):
    """Return recent pricing-engine activity for authorized dashboard routes."""

    safe_limit = max(1, min(int(limit), 200))
    connection = None

    try:
        connection = _connect()

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    actor_role,
                    actor_id,
                    action,
                    module,
                    details,
                    status,
                    duration_ms,
                    created_at
                FROM pricing_engine_activity
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (safe_limit,),
            )

            return [dict(row) for row in cursor.fetchall()]

    finally:
        if connection is not None:
            connection.close()


def fetch_activity_overview(days=30):
    """Return aggregate operational metrics without exposing individual requests."""

    safe_days = max(1, min(int(days), 365))
    connection = None

    try:
        connection = _connect()

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_events,
                    COUNT(*) FILTER (
                        WHERE status = 'SUCCESS'
                    ) AS successful_events,
                    COUNT(*) FILTER (
                        WHERE status = 'FAILURE'
                    ) AS failed_events,
                    COUNT(*) FILTER (
                        WHERE module = 'PRICING'
                        AND action IN ('QUOTE_REQUEST', 'QUOTE_COMPARE')
                    ) AS quote_requests,
                    COUNT(*) FILTER (
                        WHERE module = 'MATRIX'
                    ) AS matrix_events,
                    ROUND(
                        AVG(duration_ms)::numeric,
                        2
                    ) AS average_duration_ms,
                    percentile_cont(0.95) WITHIN GROUP (
                        ORDER BY duration_ms
                    ) AS p95_duration_ms
                FROM pricing_engine_activity
                WHERE created_at >=
                    NOW() - (%s * INTERVAL '1 day')
                """,
                (safe_days,),
            )

            overview = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT
                    module,
                    COUNT(*) AS event_count
                FROM pricing_engine_activity
                WHERE created_at >=
                    NOW() - (%s * INTERVAL '1 day')
                GROUP BY module
                ORDER BY event_count DESC
                """,
                (safe_days,),
            )

            overview["by_module"] = [
                dict(row) for row in cursor.fetchall()
            ]

            cursor.execute(
                """
                SELECT
                    action,
                    COUNT(*) AS event_count
                FROM pricing_engine_activity
                WHERE created_at >=
                    NOW() - (%s * INTERVAL '1 day')
                GROUP BY action
                ORDER BY event_count DESC
                """,
                (safe_days,),
            )

            overview["by_action"] = [
                dict(row) for row in cursor.fetchall()
            ]

            overview["period_days"] = safe_days

            return overview

    finally:
        if connection is not None:
            connection.close()