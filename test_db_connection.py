import os
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

# Get database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create FastAPI app
app = FastAPI(title="Database Connection Tester")

@app.get("/")
def root() -> Dict[str, str]:
    """
    Root endpoint that confirms the service is running.
    """
    return {"status": "online", "message": "Database connection test service is running"}

@app.get("/test-connection")
def test_connection() -> Dict[str, str]:
    """
    Test the database connection and return the result.
    """
    try:
        # Create engine without connecting
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            # Connection successful if we get here
            return {
                "status": "success",
                "message": "Successfully connected to the database",
                "database_type": engine.dialect.name
            }
    except SQLAlchemyError as e:
        # Handle database connection errors
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get port and host from environment variables or use defaults
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run("test_db_connection:app", host=HOST, port=PORT, reload=True) 