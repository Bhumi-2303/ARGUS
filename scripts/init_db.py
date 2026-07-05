#!/usr/bin/env python3
"""ARGUS Database Initialization Script.

Creates all required database tables and seeds initial configuration.
Run this script before starting the ARGUS platform for the first time.

Usage:
    python scripts/init_db.py
    
Environment:
    ARGUS_SQLITE_PATH: Path to SQLite database (default: data/argus.db)
"""

import asyncio
import sys
from pathlib import Path

# Add the root and src directories to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def main() -> None:
    """Initialize the ARGUS database schema."""
    from argus.database.engine import get_engine
    from argus.database.migrations import create_all_tables

    print("=" * 60)
    print("ARGUS Database Initialization")
    print("=" * 60)

    engine = get_engine()

    print(f"\nDatabase URL: {engine.url}")
    print("Creating tables...")

    await create_all_tables(engine)

    print("\n✓ All tables created successfully.")
    print("✓ Database is ready for use.")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("Initialization complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
