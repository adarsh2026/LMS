import asyncpg

async def connect_db():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            database="Nlibrary_db",
            user="postgres",
            password="Admin123",
            port=5432
        )
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None