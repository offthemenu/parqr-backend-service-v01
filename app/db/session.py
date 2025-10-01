from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os
import sys

# When running Alembic, skip all database setup
# Alembic creates its own engine from alembic.ini or alembic.cloud.ini
if 'alembic' in sys.argv[0]:
    # Create dummy objects to prevent import errors
    engine = None
    SessionLocal = None
else:
    # Load environment variables for normal app usage
    dotenv_path = find_dotenv()
    print("📄 .env path resolved to:", dotenv_path)
    load_dotenv(dotenv_path, override=True)
    load_dotenv()

    # Check if DATABASE_URL is provided directly (for production)
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        print("✅ Using DATABASE_URL from environment")
    else:
        # Fallback to individual database environment variables (for development)
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        print(f"Sanity Check: {DB_USER=}")

        if not all([DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT]):
            raise ValueError("Missing required database environment variables. Either provide DATABASE_URL or all of: DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT")

        DATABASE_URL = f"mysql+mysqldb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    print("✅ Database configured successfully")