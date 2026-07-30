import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise Exception("DB_URL environment variable is not set.")

conn = psycopg2.connect(DB_URL)
conn.autocommit = True
cur = conn.cursor()

# Make sure the migration tracking table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

migrations_dir = Path("migrations")

migration_files = sorted(migrations_dir.glob("*.sql"))

for migration in migration_files:
    version = migration.name

    cur.execute(
        "SELECT 1 FROM schema_migrations WHERE version = %s",
        (version,)
    )

    if cur.fetchone():
        print(f"✓ {version} already applied")
        continue

    print(f"Applying {version}...")

    with open(migration, "r", encoding="utf-8") as f:
        sql = f.read().strip()

    if not sql:
        print(f"✓ {version} is empty, skipping.")
        cur.execute(
            "INSERT INTO schema_migrations(version) VALUES (%s)",
            (version,)
        )
        continue

    try:
        cur.execute(sql)

        cur.execute(
            "INSERT INTO schema_migrations(version) VALUES (%s)",
            (version,)
        )

        print(f"✓ Applied {version}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Failed on {version}")
        print(e)
        raise

cur.close()
conn.close()

print("\nAll migrations completed successfully.")