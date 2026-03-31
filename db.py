import asyncpg

async def create_pool():
    pool = await asyncpg.create_pool(
        host="localhost",
        database="Nlibrary_db",
        user="postgres",
        password="Admin123",
        port=5432,
        min_size=1,
        max_size=10
    )
    return pool