"""
Batch Judge Profile Analysis Script

Fetches all judges and their opinions from the database,
runs JudgeProfiler analysis, and saves profiles to disk.
"""

import os
import asyncio
import asyncpg
import json
from judge_analysis_model import JudgeProfiler

POSTGRES_DSN = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
MODEL_DIR = "./models"

async def fetch_judges_and_opinions(conn):
    judges = await conn.fetch("SELECT id FROM judges")
    judge_opinions = {}
    for record in judges:
        judge_id = str(record["id"])
        opinions = await conn.fetch(
            "SELECT * FROM opinions WHERE author_id = $1", judge_id
        )
        # Convert asyncpg Record to dict
        opinions_dicts = [dict(op) for op in opinions]
        judge_opinions[judge_id] = opinions_dicts
    return judge_opinions

async def main():
    conn = await asyncpg.connect(POSTGRES_DSN)
    profiler = JudgeProfiler(model_dir=MODEL_DIR)
    judge_opinions = await fetch_judges_and_opinions(conn)
    for judge_id, opinions in judge_opinions.items():
        if len(opinions) < 5:
            print(f"Skipping judge {judge_id}: not enough opinions")
            continue
        profile = profiler.analyze_judge(judge_id, opinions)
        print(f"Profiled judge {judge_id} ({len(opinions)} opinions)")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
