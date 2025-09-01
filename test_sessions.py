#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('backend')

from app.core.database import engine
from sqlalchemy import text

async def check_sessions():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT id, status FROM sessions LIMIT 5'))
            rows = result.fetchall()
            print("Znalezione sesje:")
            for row in rows:
                print(f"ID: {row[0]}, Status: {row[1]}")
            return rows
    except Exception as e:
        print(f"Błąd: {e}")
        return []

if __name__ == "__main__":
    asyncio.run(check_sessions())
