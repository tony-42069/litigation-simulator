"""
User management script for the Litigation Simulator.

This script provides functionality to create, list, and manage users in the database.
"""

import asyncio
import logging
import os
from datetime import datetime

import asyncpg
from dotenv import load_dotenv

from auth import get_password_hash

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection string
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "litigation_simulator")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

POSTGRES_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

async def create_user(
    username: str,
    email: str,
    password: str,
    full_name: str = None,
    organization: str = None,
    role: str = "user",
    subscription_tier: str = "basic"
):
    """
    Create a new user in the database.
    
    Args:
        username: Username
        email: Email address
        password: Plain text password
        full_name: Full name
        organization: Organization
        role: User role (user, admin)
        subscription_tier: Subscription tier (basic, professional, enterprise)
        
    Returns:
        Newly created user ID
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    
    try:
        # Hash the password
        password_hash = get_password_hash(password)
        
        # Get current datetime
        now = datetime.utcnow()
        
        # Check if user exists
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = $2",
            username, email
        )
        
        if existing_user:
            logger.error(f"User already exists with username {username} or email {email}")
            return None
        
        # Insert the user
        user_id = await conn.fetchval(
            """
            INSERT INTO users (
                username, email, password_hash, full_name, organization,
                role, created_at, subscription_tier, is_active
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            """,
            username, email, password_hash, full_name, organization,
            role, now, subscription_tier, True
        )
        
        logger.info(f"Created user {username} with ID {user_id}")
        
        return user_id
        
    finally:
        await conn.close()

async def list_users():
    """
    List all users in the database.
    """
    conn = await asyncpg.connect(POSTGRES_DSN)
    
    try:
        users = await conn.fetch(
            """
            SELECT id, username, email, full_name, organization, role, 
                   created_at, last_login, subscription_tier, is_active
            FROM users
            ORDER BY id
            """
        )
        
        logger.info(f"Found {len(users)} users")
        
        print("\nUser List:")
        print("=" * 80)
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")
            print(f"Subscription: {user['subscription_tier']}")
            print(f"Created: {user['created_at']}")
            print(f"Active: {user['is_active']}")
            print("-" * 80)
            
    finally:
        await conn.close()

async def create_admin_user():
    """
    Create an admin user for the application.
    """
    # Get inputs with defaults
    username = input("Admin username (default: admin): ") or "admin"
    email = input("Admin email (default: admin@example.com): ") or "admin@example.com"
    password = input("Admin password (default: adminpassword): ") or "adminpassword"
    full_name = input("Full name (default: Administrator): ") or "Administrator"
    
    user_id = await create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role="admin",
        subscription_tier="enterprise"
    )
    
    if user_id:
        logger.info(f"Created admin user {username} with ID {user_id}")
    else:
        logger.error("Failed to create admin user")

async def main():
    """
    Main entry point for user management.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="User management for Litigation Simulator")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Create user parser
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("--username", required=True, help="Username")
    create_parser.add_argument("--email", required=True, help="Email address")
    create_parser.add_argument("--password", required=True, help="Password")
    create_parser.add_argument("--full-name", help="Full name")
    create_parser.add_argument("--organization", help="Organization")
    create_parser.add_argument("--role", choices=["user", "admin"], default="user", help="User role")
    create_parser.add_argument("--subscription", choices=["basic", "professional", "enterprise"], 
                             default="basic", help="Subscription tier")
    
    # Create admin parser
    admin_parser = subparsers.add_parser("create-admin", help="Create an admin user (interactive)")
    
    # List users parser
    list_parser = subparsers.add_parser("list", help="List all users")
    
    args = parser.parse_args()
    
    if args.command == "create":
        await create_user(
            username=args.username,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            organization=args.organization,
            role=args.role,
            subscription_tier=args.subscription
        )
    elif args.command == "create-admin":
        await create_admin_user()
    elif args.command == "list":
        await list_users()
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 