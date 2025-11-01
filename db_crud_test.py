import psycopg2
from psycopg2 import sql
import sys

# Database connection parameters
params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'litigation_simulator',
    'user': 'postgres',
    'password': 'Teqifjarobt$$44'
}

def connect():
    """Connect to the PostgreSQL database server"""
    try:
        # Connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        print('Connection successful!')
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        sys.exit(1)

def create_tables(conn):
    """Create test tables in the PostgreSQL database"""
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # First drop the table if it exists
        cur.execute("DROP TABLE IF EXISTS judges")
        print("Dropped existing judges table if it existed.")
        
        # Execute a command to create table
        cur.execute("""
            CREATE TABLE judges (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                court VARCHAR(255),
                position VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Commit the changes
        conn.commit()
        
        # Close cursor
        cur.close()
        print("Judges table created successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating tables: {error}")

def insert_judge(conn, name, court, position):
    """Insert a new judge into the judges table"""
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a command to insert data
        cur.execute(
            "INSERT INTO judges (name, court, position) VALUES (%s, %s, %s) RETURNING id",
            (name, court, position)
        )
        
        # Get the generated id
        judge_id = cur.fetchone()[0]
        
        # Commit the changes
        conn.commit()
        
        # Close cursor
        cur.close()
        print(f"Judge inserted with ID: {judge_id}")
        return judge_id
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting judge: {error}")
        # Roll back if there's an issue
        conn.rollback()

def get_judges(conn):
    """Query all judges from the judges table"""
    try:
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a command to query data
        cur.execute("SELECT id, name, court, position FROM judges ORDER BY name")
        
        # Fetch all rows
        rows = cur.fetchall()
        
        print("List of judges:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Court: {row[2]}, Position: {row[3]}")
        
        # Close cursor
        cur.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error querying judges: {error}")

def main():
    # Connect to the database
    conn = connect()
    
    # Create tables
    create_tables(conn)
    
    # Insert sample judges
    insert_judge(conn, "John Roberts", "Supreme Court", "Chief Justice")
    insert_judge(conn, "Sonia Sotomayor", "Supreme Court", "Associate Justice")
    insert_judge(conn, "Ketanji Brown Jackson", "Supreme Court", "Associate Justice")
    
    # Query judges
    get_judges(conn)
    
    # Close the connection
    conn.close()
    print("Database connection closed.")

if __name__ == '__main__':
    main() 