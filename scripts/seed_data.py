#!/usr/bin/env python3
"""ARGUS Development Data Seeder.

Populates the database with realistic sample data for development
and testing purposes. Creates sample tasks, agents, audit entries,
and metrics data.

Usage:
    python scripts/seed_data.py

Warning:
    This script is for DEVELOPMENT ONLY. Never run in production.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main() -> None:
    """Seed the ARGUS database with development data."""
    from argus.database.engine import get_engine
    from argus.database.migrations import create_all_tables
    from argus.database.session import async_session_factory
    from argus.database.models import TaskRecord, AgentRecord, AuditRecord, MetricRecord

    print("=" * 60)
    print("ARGUS Development Data Seeder")
    print("=" * 60)

    engine = get_engine()
    await create_all_tables(engine)
    session_factory = async_session_factory(engine)

    now = datetime.now(timezone.utc)

    async with session_factory() as session:
        # --- Seed Agent Records ---
        agents = [
            AgentRecord(
                agent_id=str(uuid4()),
                name="data_intelligence",
                version="0.1.0",
                status="ready",
                capabilities="data_ingestion,data_normalization,data_correlation",
                registered_at=now - timedelta(hours=2),
                last_heartbeat=now,
            ),
            AgentRecord(
                agent_id=str(uuid4()),
                name="threat_analysis",
                version="0.1.0",
                status="ready",
                capabilities="threat_detection,mitre_mapping,anomaly_detection",
                registered_at=now - timedelta(hours=2),
                last_heartbeat=now,
            ),
            AgentRecord(
                agent_id=str(uuid4()),
                name="knowledge_context",
                version="0.1.0",
                status="ready",
                capabilities="knowledge_retrieval,context_enrichment,incident_correlation",
                registered_at=now - timedelta(hours=2),
                last_heartbeat=now,
            ),
            AgentRecord(
                agent_id=str(uuid4()),
                name="risk_prediction",
                version="0.1.0",
                status="idle",
                capabilities="risk_scoring,risk_prediction,vulnerability_assessment",
                registered_at=now - timedelta(hours=2),
                last_heartbeat=now - timedelta(minutes=5),
            ),
            AgentRecord(
                agent_id=str(uuid4()),
                name="decision_support",
                version="0.1.0",
                status="ready",
                capabilities="recommendation,decision_synthesis,incident_response",
                registered_at=now - timedelta(hours=2),
                last_heartbeat=now,
            ),
        ]
        session.add_all(agents)

        # --- Seed Task Records ---
        tasks = [
            TaskRecord(
                task_id=str(uuid4()),
                task_type="data_ingestion",
                status="completed",
                priority="medium",
                agent_id=agents[0].agent_id,
                created_at=now - timedelta(minutes=45),
                started_at=now - timedelta(minutes=44),
                completed_at=now - timedelta(minutes=42),
                result='{"records_processed": 1500, "anomalies_found": 3}',
            ),
            TaskRecord(
                task_id=str(uuid4()),
                task_type="threat_analysis",
                status="running",
                priority="high",
                agent_id=agents[1].agent_id,
                created_at=now - timedelta(minutes=10),
                started_at=now - timedelta(minutes=9),
            ),
            TaskRecord(
                task_id=str(uuid4()),
                task_type="risk_assessment",
                status="pending",
                priority="critical",
                created_at=now - timedelta(minutes=2),
            ),
        ]
        session.add_all(tasks)

        # --- Seed Audit Records ---
        audits = [
            AuditRecord(
                audit_id=str(uuid4()),
                timestamp=now - timedelta(minutes=30),
                actor="system",
                action="agent_registered",
                resource="data_intelligence",
                outcome="success",
                details="Agent registered successfully",
            ),
            AuditRecord(
                audit_id=str(uuid4()),
                timestamp=now - timedelta(minutes=15),
                actor="admin",
                action="config_updated",
                resource="security.rate_limit",
                outcome="success",
                details="Rate limit updated to 200 req/min",
            ),
        ]
        session.add_all(audits)

        # --- Seed Metric Records ---
        for i in range(24):
            metric_time = now - timedelta(hours=24 - i)
            session.add(
                MetricRecord(
                    metric_id=str(uuid4()),
                    name="system_health_score",
                    value=85.0 + (i * 0.5),
                    timestamp=metric_time,
                    labels='{"component": "overall"}',
                )
            )

        await session.commit()

    print("✓ Seeded 5 agent records")
    print("✓ Seeded 3 task records")
    print("✓ Seeded 2 audit records")
    print("✓ Seeded 24 metric records")
    print("\nDevelopment data seeded successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
