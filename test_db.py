"""
Simple FastAPI application to test database connectivity.
Only uses essential dependencies.
"""

import os
from fastapi import FastAPI, Depends, HTTPException
import asyncpg
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Load environment variables
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'Teqifjarobt$$44')}@localhost:5432/{os.getenv('POSTGRES_DB', 'litigation_simulator')}"

app = FastAPI(title="Litigation Simulator - DB Test")

# Database connection pool
async def get_db_pool():
    pool = await asyncpg.create_pool(DATABASE_URL)
    try:
        yield pool
    finally:
        await pool.close()

# Models
class Judge(BaseModel):
    id: str
    name: str
    position: Optional[str] = None
    court: Optional[str] = None

# Routes
@app.get("/")
def read_root():
    return {"message": "Litigation Simulator API is running"}

@app.get("/health")
async def health_check(pool = Depends(get_db_pool)):
    try:
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            return {
                "status": "healthy",
                "database": "connected",
                "version": version
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/judges", response_model=List[Judge])
async def get_judges(limit: int = 10, pool = Depends(get_db_pool)):
    try:
        async with pool.acquire() as conn:
            judges = await conn.fetch(
                """
                SELECT id, name, position, court 
                FROM judges 
                ORDER BY name 
                LIMIT $1
                """, 
                limit
            )
            return [dict(judge) for judge in judges]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch judges: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("test_db:app", host="0.0.0.0", port=8000, reload=True) 