"""
Database initialization script for the Litigation Simulator.

This script connects to the PostgreSQL database and creates all the necessary tables
by executing the SQL statements in schema.sql.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection parameters
db_params = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Teqifjarobt$$44'),
    'database': os.getenv('POSTGRES_DB', 'litigation_simulator')
}

def create_database_if_not_exists(params):
    """Create the database if it doesn't exist."""
    # Connect to PostgreSQL server
    db_name = params.pop('database')
    conn = None
    
    try:
        logger.info("Connecting to PostgreSQL server to check if database exists...")
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Database '{db_name}' created successfully")
        else:
            logger.info(f"Database '{db_name}' already exists")
            
        cursor.close()
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
    
    # Add the database back to the parameters
    params['database'] = db_name
    return params

def initialize_database(params):
    """Initialize the database with the schema from schema.sql."""
    conn = None
    try:
        logger.info("Connecting to database to create schema...")
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        with open('schema.sql', 'r') as file:
            schema_sql = file.read()
            logger.info("Executing schema.sql...")
            cursor.execute(schema_sql)
        
        conn.commit()
        logger.info("Database schema created successfully")
        
        # Insert a sample judge for testing
        cursor.execute("""
            INSERT INTO judges (name, court, position) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """, ("John Roberts", "Supreme Court", "Chief Justice"))
        
        judge_id = cursor.fetchone()
        if judge_id:
            logger.info(f"Sample judge created with ID: {judge_id[0]}")
            
            # Insert sample analytics for this judge
            cursor.execute("""
                INSERT INTO judge_analytics (judge_id, writing_style, ruling_patterns) 
                VALUES (%s, %s, %s)
                ON CONFLICT (judge_id) DO NOTHING
            """, (
                judge_id[0], 
                '{"formality": 0.85, "complexity": 0.78, "clarity": 0.72}',
                '{"conservative": 0.65, "liberal": 0.35, "commercial_favored": 0.55, "regulatory_favored": 0.45}'
            ))
            
        conn.commit()
        logger.info("Sample data inserted successfully")
        
        cursor.close()
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def main():
    """Main function to initialize the database."""
    logger.info("Starting database initialization...")
    
    try:
        # First ensure the database exists
        params = create_database_if_not_exists(db_params.copy())
        
        # Then initialize the schema
        initialize_database(params)
        
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 