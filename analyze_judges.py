"""
Judge Analysis Tool

This script analyzes and processes judge data from the Court Listener API,
generates insights, and stores the results in the database.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

import asyncpg
from dotenv import load_dotenv

from court_listener_api_integration import CourtListenerAPI
from judge_analysis_model import JudgeProfiler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection parameters
POSTGRES_DSN = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

async def store_judge_analytics(conn, judge_id: str, analysis_type: str, analysis_data: Dict[str, Any], confidence: float = 0.0):
    """
    Store judge analytics in the database.
    
    Args:
        conn: Database connection
        judge_id: Court Listener ID of the judge
        analysis_type: Type of analysis (e.g., 'writing_style', 'topic', 'ruling_pattern')
        analysis_data: Analysis data to store
        confidence: Confidence score for the analysis
    """
    now = datetime.utcnow()
    
    # Check if analysis already exists
    existing = await conn.fetchrow(
        "SELECT id FROM judge_analytics WHERE judge_id = $1 AND analysis_type = $2",
        judge_id, analysis_type
    )
    
    if existing:
        # Update existing analysis
        await conn.execute(
            """
            UPDATE judge_analytics
            SET analysis_data = $1, confidence = $2, updated_at = $3
            WHERE judge_id = $4 AND analysis_type = $5
            """,
            json.dumps(analysis_data), confidence, now, judge_id, analysis_type
        )
        logger.info(f"Updated {analysis_type} analysis for judge {judge_id}")
    else:
        # Insert new analysis
        await conn.execute(
            """
            INSERT INTO judge_analytics (judge_id, analysis_type, analysis_data, confidence, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            judge_id, analysis_type, json.dumps(analysis_data), confidence, now, now
        )
        logger.info(f"Stored new {analysis_type} analysis for judge {judge_id}")

async def store_judge_pattern(conn, judge_id: str, pattern_type: str, pattern_data: Dict[str, Any], source_count: int, confidence: float = 0.0):
    """
    Store judge patterns in the database.
    
    Args:
        conn: Database connection
        judge_id: Court Listener ID of the judge
        pattern_type: Type of pattern (e.g., 'questioning', 'citation', 'reasoning')
        pattern_data: Pattern data to store
        source_count: Number of sources used for the analysis
        confidence: Confidence score for the pattern
    """
    now = datetime.utcnow()
    
    # Check if pattern already exists
    existing = await conn.fetchrow(
        "SELECT id FROM judge_patterns WHERE judge_id = $1 AND pattern_type = $2",
        judge_id, pattern_type
    )
    
    if existing:
        # Update existing pattern
        await conn.execute(
            """
            UPDATE judge_patterns
            SET pattern_data = $1, source_count = $2, confidence = $3, updated_at = $4
            WHERE judge_id = $5 AND pattern_type = $6
            """,
            json.dumps(pattern_data), source_count, confidence, now, judge_id, pattern_type
        )
        logger.info(f"Updated {pattern_type} pattern for judge {judge_id}")
    else:
        # Insert new pattern
        await conn.execute(
            """
            INSERT INTO judge_patterns (judge_id, pattern_type, pattern_data, source_count, confidence, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            judge_id, pattern_type, json.dumps(pattern_data), source_count, confidence, now, now
        )
        logger.info(f"Stored new {pattern_type} pattern for judge {judge_id}")

async def analyze_judge(judge_id: str, opinion_limit: int = 50):
    """
    Analyze a judge's writing style, topics, and ruling patterns.
    
    Args:
        judge_id: Court Listener ID of the judge
        opinion_limit: Maximum number of opinions to analyze
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    
    try:
        # Initialize the judge profiler
        profiler = JudgeProfiler()
        
        # Get judge details
        judge = await conn.fetchrow("SELECT * FROM judges WHERE id = $1", judge_id)
        
        if not judge:
            logger.error(f"Judge {judge_id} not found in database")
            return
        
        logger.info(f"Analyzing judge: {judge['name']} (ID: {judge_id})")
        
        # Get opinions
        opinions = await conn.fetch(
            """
            SELECT o.*, c.case_name, c.case_type, c.nature_of_suit
            FROM opinions o
            JOIN cases c ON o.case_id = c.id
            WHERE o.author_id = $1
            ORDER BY o.date_filed DESC
            LIMIT $2
            """,
            judge_id, opinion_limit
        )
        
        # Convert to list of dictionaries
        opinion_data = [dict(op) for op in opinions]
        
        if not opinion_data:
            logger.warning(f"No opinions found for judge {judge_id}")
            return
        
        logger.info(f"Found {len(opinion_data)} opinions for analysis")
        
        # Analyze writing style
        try:
            writing_style = profiler.analyze_writing_style(opinion_data)
            await store_judge_analytics(conn, judge_id, "writing_style", writing_style, 0.85)
        except Exception as e:
            logger.error(f"Error analyzing writing style: {e}")
        
        # Extract topics
        try:
            topics = profiler.extract_topics(opinion_data)
            await store_judge_analytics(conn, judge_id, "topics", topics, 0.8)
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
        
        # Train ruling classifier
        try:
            ruling_patterns = profiler.train_ruling_classifier(opinion_data)
            await store_judge_analytics(conn, judge_id, "ruling_patterns", ruling_patterns, 0.75)
        except Exception as e:
            logger.error(f"Error training ruling classifier: {e}")
        
        # Analyze questioning patterns from oral arguments
        oral_arguments = await conn.fetch(
            """
            SELECT oa.*, c.case_name, c.case_type
            FROM oral_arguments oa
            JOIN cases c ON oa.case_id = c.id
            WHERE oa.panel::jsonb @> $1::jsonb
            ORDER BY oa.date_argued DESC
            LIMIT 25
            """,
            json.dumps([judge_id])
        )
        
        oral_argument_data = [dict(oa) for oa in oral_arguments]
        
        if oral_argument_data:
            logger.info(f"Found {len(oral_argument_data)} oral arguments for analysis")
            try:
                questioning_patterns = profiler.analyze_judge_questioning(judge_id, oral_argument_data)
                await store_judge_pattern(
                    conn, 
                    judge_id, 
                    "questioning", 
                    questioning_patterns["patterns"], 
                    len(oral_argument_data),
                    0.7
                )
            except Exception as e:
                logger.error(f"Error analyzing questioning patterns: {e}")
        else:
            logger.warning(f"No oral arguments found for judge {judge_id}")
        
        logger.info(f"Analysis complete for judge {judge_id}")
        
    finally:
        await conn.close()

async def analyze_all_judges(limit: int = 10, opinion_min: int = 10):
    """
    Analyze all judges with a minimum number of opinions.
    
    Args:
        limit: Maximum number of judges to analyze
        opinion_min: Minimum number of opinions required for analysis
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    
    try:
        # Get judges with at least opinion_min opinions
        judges = await conn.fetch(
            """
            SELECT j.id, j.name, COUNT(o.id) as opinion_count
            FROM judges j
            JOIN opinions o ON j.id = o.author_id
            GROUP BY j.id, j.name
            HAVING COUNT(o.id) >= $1
            ORDER BY COUNT(o.id) DESC
            LIMIT $2
            """,
            opinion_min, limit
        )
        
        logger.info(f"Found {len(judges)} judges with at least {opinion_min} opinions")
        
        for judge in judges:
            logger.info(f"Processing judge {judge['name']} with {judge['opinion_count']} opinions")
            await analyze_judge(judge['id'])
            
    finally:
        await conn.close()

async def main():
    """Main entry point"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Analyze judges from Court Listener data")
    parser.add_argument("--judge-id", help="Analyze a specific judge by ID")
    parser.add_argument("--all", action="store_true", help="Analyze all judges")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of judges to analyze")
    parser.add_argument("--opinion-min", type=int, default=10, help="Minimum opinions required for analysis")
    
    args = parser.parse_args()
    
    if args.judge_id:
        await analyze_judge(args.judge_id)
    elif args.all:
        await analyze_all_judges(args.limit, args.opinion_min)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
