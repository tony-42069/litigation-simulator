"""
Initial Court Listener Data Import Script

This script fetches judges, their opinions, and oral arguments from the Court Listener API
and inserts them into the local PostgreSQL database for the Litigation Simulator project.
"""

import os
import asyncio
import asyncpg
import json
from court_listener_api_integration import CourtListenerAPI

POSTGRES_DSN = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
BATCH_SIZE = 20  # Number of records to fetch per API call

async def insert_judge(conn, judge):
    # Convert all IDs to strings
    judge_id = str(judge.get("id"))
    court_id = str(judge.get("court_id")) if judge.get("court_id") else None
    
    # Ensure required fields have values
    name = judge.get("name") or "Unknown Judge"
    position = judge.get("position") or "Judge"
    court = judge.get("court") or "Unknown Court"
    
    await conn.execute("""
        INSERT INTO judges (id, name, position, court, court_id, appointed_date, birth_year, education, prior_positions, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (id) DO NOTHING
    """, judge_id, name, position, court, court_id,
         judge.get("appointed_date"), judge.get("birth_year"), judge.get("education"), judge.get("prior_positions"),
         json.dumps(judge))

async def insert_opinion(conn, opinion, judge_id):
    # Convert IDs to strings and handle nulls
    opinion_id = str(opinion.get("id"))
    case_id = str(opinion.get("case_id")) if opinion.get("case_id") else None
    judge_id = str(judge_id)
    
    # Ensure required fields have values
    text = opinion.get("text") or ""
    opinion_type = opinion.get("type") or "opinion"
    
    # Parse date or use default
    try:
        date_filed = datetime.strptime(opinion.get("date_filed"), "%Y-%m-%d").date() if opinion.get("date_filed") else datetime(1970, 1, 1).date()
    except ValueError:
        date_filed = datetime(1970, 1, 1).date()
    
    await conn.execute("""
        INSERT INTO opinions (id, case_id, author_id, date_filed, type, text, text_length, citation, precedential, citation_count, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO NOTHING
    """, opinion_id, case_id, judge_id, date_filed, opinion_type,
         text, len(text), opinion.get("citation"), opinion.get("precedential", False),
         opinion.get("citation_count", 0), json.dumps(opinion))

async def main():
    conn = await asyncpg.connect(POSTGRES_DSN)
    async with CourtListenerAPI() as api:
        offset = 0
        while True:
            judges_data = await api.search_judges(limit=BATCH_SIZE, offset=offset)
            judges = judges_data.get("results", [])
            if not judges:
                break
            for judge in judges:
                await insert_judge(conn, judge)
                judge_id = judge.get("id")
                # Fetch opinions for this judge
                opinions_data = await api.search_opinions(judge_id=judge_id, limit=BATCH_SIZE)
                for op in opinions_data.get("results", []):
                    # Download full text if available
                    try:
                        op["text"] = await api.download_opinion_text(op["id"])
                    except Exception:
                        op["text"] = ""
                    await insert_opinion(conn, op, judge_id)
            offset += BATCH_SIZE
            print(f"Imported {offset} judges...")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
