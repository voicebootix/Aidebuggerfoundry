import asyncpg
import os
import asyncio

async def main():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    await conn.execute(
        "INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified) "
        "VALUES ('00000000-0000-0000-0000-000000000001', 'demo@example.com', '', 'Demo User', true, true) "
        "ON CONFLICT (id) DO NOTHING;"
    )
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main()) 