import os
import asyncio
import asyncpg

MIGRATIONS = [
    {
        "table": "voice_conversations",
        "column": "strategy_validated",
        "type": "BOOLEAN DEFAULT FALSE",
        "sql": "ALTER TABLE voice_conversations ADD COLUMN strategy_validated BOOLEAN DEFAULT FALSE;"
    },
    {
        "table": "dream_sessions",
        "column": "project_id",
        "type": "UUID REFERENCES projects(id) ON DELETE CASCADE",
        "sql": "ALTER TABLE dream_sessions ADD COLUMN project_id UUID REFERENCES projects(id) ON DELETE CASCADE;"
    }
]

async def column_exists(conn, table, column):
    result = await conn.fetchval(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = $1 AND column_name = $2
        """, table, column
    )
    return result is not None

async def run_migrations():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL environment variable not set.")
        return
    conn = await asyncpg.connect(db_url)
    try:
        for mig in MIGRATIONS:
            if await column_exists(conn, mig["table"], mig["column"]):
                print(f"✅ Column '{mig['column']}' already exists in '{mig['table']}'. Skipping.")
            else:
                try:
                    await conn.execute(mig["sql"])
                    print(f"✅ Added column '{mig['column']}' to '{mig['table']}'.")
                except Exception as e:
                    print(f"❌ Failed to add column '{mig['column']}' to '{mig['table']}': {e}")
        print("\n🎉 Migration complete!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migrations()) 