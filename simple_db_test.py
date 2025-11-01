import psycopg2
import sys

# Database connection parameters
params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'litigation_simulator',
    'user': 'postgres',
    'password': 'Teqifjarobt$$44'
}

print("Attempting to connect to PostgreSQL database...")
print(f"Connection parameters: host={params['host']}, port={params['port']}, db={params['database']}, user={params['user']}")

try:
    # Establish connection
    conn = psycopg2.connect(**params)
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a test query
    cur.execute("SELECT version();")
    
    # Fetch the result
    version = cur.fetchone()[0]
    print("Connection successful!")
    print(f"PostgreSQL version: {version}")
    
    # Close cursor and connection
    cur.close()
    conn.close()
    
    print("Connection closed.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 