import os
import asyncio
import asyncpg

MIGRATIONS = [
    {
        "table": "voice_conversations",
        "column": "strategy_validated",
        "type": "BOOLEAN DEFAULT FALSE",
        "sql": "ALTER TABLE voice_conversations ADD COLUMN strategy_validated BOOLEAN DEFAULT FALSE;"
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

async def all_project_ids_are_uuids(conn):
    rows = await conn.fetch("SELECT id FROM projects WHERE id !~* '^[0-9a-fA-F-]{36}$';")
    return len(rows) == 0

async def convert_projects_id_to_uuid(conn):
    print("Converting projects.id from VARCHAR to UUID...")
    await conn.execute("ALTER TABLE projects ALTER COLUMN id TYPE uuid USING id::uuid;")
    print("✅ projects.id column converted to UUID.")

async def add_project_id_to_dream_sessions(conn):
    print("Adding project_id column to dream_sessions...")
    await conn.execute("ALTER TABLE dream_sessions ADD COLUMN project_id UUID REFERENCES projects(id) ON DELETE CASCADE;")
    print("✅ project_id column added to dream_sessions.")

async def run_migrations():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL environment variable not set.")
        return
    conn = await asyncpg.connect(db_url)
    try:
        # Run standard migrations
        for mig in MIGRATIONS:
            if await column_exists(conn, mig["table"], mig["column"]):
                print(f"✅ Column '{mig['column']}' already exists in '{mig['table']}'. Skipping.")
            else:
                try:
                    await conn.execute(mig["sql"])
                    print(f"✅ Added column '{mig['column']}' to '{mig['table']}'.")
                except Exception as e:
                    print(f"❌ Failed to add column '{mig['column']}' to '{mig['table']}': {e}")

        # Handle dream_sessions.project_id migration
        if await column_exists(conn, "dream_sessions", "project_id"):
            print("✅ Column 'project_id' already exists in 'dream_sessions'. Skipping.")
        else:
            print("Checking if all projects.id values are valid UUIDs...")
            if await all_project_ids_are_uuids(conn):
                try:
                    await convert_projects_id_to_uuid(conn)
                    await add_project_id_to_dream_sessions(conn)
                except Exception as e:
                    print(f"❌ Migration failed: {e}")
            else:
                print("❌ Migration aborted: Some projects.id values are not valid UUIDs. Please fix them manually.")
        print("\n🎉 Migration complete!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migrations()) 